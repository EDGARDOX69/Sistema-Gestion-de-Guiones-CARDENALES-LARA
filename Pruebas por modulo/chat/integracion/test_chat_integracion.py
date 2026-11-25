"""CP-CHA-INT-01: asistente por reglas, historial y aislamiento por usuario."""

from app.model.chat_model import ChatModel
from soporte_api import cliente_anonimo, login_como


def test_asistente_anonimo_devuelve_401(app):
    respuesta = cliente_anonimo(app).get('/asistente/')
    assert respuesta.status_code == 401
    assert respuesta.get_json()['error'] == 'No autenticado'


def test_mensaje_valido_guarda_historial(app, crear_usuario, db):
    usuario = crear_usuario(rol='Usuario')
    cliente = login_como(app, usuario)

    respuesta = cliente.get('/asistente/')
    assert respuesta.status_code == 200
    assert respuesta.get_json()['historial'] == []

    respuesta = cliente.post('/asistente/', data={'mensaje': '   '})
    assert respuesta.status_code == 400

    respuesta = cliente.post('/asistente/', data={'mensaje': 'Hola, necesito ayuda'})
    assert respuesta.status_code == 200
    assert respuesta.get_json()['respuesta']

    with db.cursor() as cur:
        cur.execute(
            'SELECT mensaje_usuario, respuesta_ia, contexto '
            'FROM historial_chat WHERE usuario_id = %s',
            (usuario.id,),
        )
        fila = cur.fetchone()
    assert fila is not None
    assert fila['mensaje_usuario'] == 'Hola, necesito ayuda'
    assert fila['respuesta_ia']
    assert fila['contexto']


def test_historial_no_mezcla_usuarios_y_limita_a_20(app, crear_usuario):
    usuario_a = crear_usuario(rol='Usuario')
    usuario_b = crear_usuario(rol='Usuario')
    modelo = ChatModel()

    for i in range(25):
        assert modelo.guardar(usuario_a.id, f'Mensaje {i}', f'Respuesta {i}')
    assert modelo.guardar(usuario_b.id, 'Solo de B', 'Respuesta B')

    cliente_b = login_como(app, usuario_b)
    respuesta = cliente_b.get('/asistente/')
    historial_b = respuesta.get_json()['historial']
    assert len(historial_b) == 1
    assert historial_b[0]['mensaje_usuario'] == 'Solo de B'

    cliente_a = login_como(app, usuario_a)
    respuesta = cliente_a.get('/asistente/')
    historial_a = respuesta.get_json()['historial']
    assert len(historial_a) == 20
    assert all(not item['mensaje_usuario'].startswith('Solo de B') for item in historial_a)
