"""CP-NOT-INT-01: aislamiento de las notificaciones por usuario."""

from app.model.notificacion_model import NotificacionModel
from soporte_api import cliente_anonimo, login_como


def test_una_notificacion_ajena_no_se_puede_leer(
    app, crear_usuario, seguridad_db
):
    duenio = crear_usuario(rol='Usuario')
    intruso = crear_usuario(rol='Usuario')
    notificacion_id = NotificacionModel().crear(
        duenio.id, 'tarea_asignada', 'Prueba', 'Mensaje de prueba',
        '/gestion-tarea/mis-tareas',
    )
    assert notificacion_id is not None

    cliente = login_como(app, intruso)
    respuesta = cliente.get('/notificaciones/api')
    assert respuesta.status_code == 200
    assert respuesta.get_json()['count'] == 0
    assert respuesta.get_json()['items'] == []

    respuesta = cliente.post('/notificaciones/leer', data={'id': notificacion_id})
    assert respuesta.status_code == 200
    assert respuesta.get_json()['success'] is False

    respuesta = cliente.post('/notificaciones/leer-todas')
    assert respuesta.status_code == 200

    with seguridad_db.cursor() as cur:
        cur.execute('SELECT leida FROM notificaciones WHERE id = %s', (notificacion_id,))
        assert cur.fetchone()['leida'] == 0

    cliente = login_como(app, duenio)
    respuesta = cliente.get('/notificaciones/api')
    assert respuesta.get_json()['count'] == 1

    respuesta = cliente.post('/notificaciones/leer', data={'id': notificacion_id})
    assert respuesta.get_json()['success'] is True

    with seguridad_db.cursor() as cur:
        cur.execute('SELECT leida FROM notificaciones WHERE id = %s', (notificacion_id,))
        assert cur.fetchone()['leida'] == 1


def test_api_anonima_redirige_al_login(app):
    respuesta = cliente_anonimo(app).get('/notificaciones/api')
    assert respuesta.status_code == 302
    assert '/auth/login' in respuesta.headers['Location']


def test_id_invalido_devuelve_400(app, crear_usuario):
    usuario = crear_usuario(rol='Usuario')
    cliente = login_como(app, usuario)

    assert cliente.post('/notificaciones/leer', data={'id': 'abc'}).status_code == 400
    assert cliente.post('/notificaciones/leer', data={}).status_code == 400
