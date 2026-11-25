"""GU-AT — Prueba de aceptación del flujo completo de un guion.

Representa lo que hace el operador un día de juego:
crear guion -> cargar pregame y game -> previsualizar -> publicar ->
iniciar EN VIVO -> avanzar -> retroceder -> finalizar.

Si esta prueba pasa, el módulo cumple el recorrido de negocio completo.
"""
import uuid

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.db]


def _db(esquema='estadio_db'):
    from app.database import Database
    return Database.get_connection(esquema)


def _elementos(guion_id):
    from app.model.guion_model import ElementoGuionModel
    pregame, game = ElementoGuionModel().obtener_por_guion_ordenados(guion_id)
    return pregame + game


def _estados(guion_id):
    db = _db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT id, estado FROM elementos_guion WHERE guion_id = %s ORDER BY id",
            (guion_id,),
        )
        return {fila['id']: fila['estado'] for fila in cur.fetchall()}


def _cerrar_guiones_en_vivo():
    db = _db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE guiones SET estado = 'finalizado', inicio_show = NULL "
            "WHERE estado = 'en_vivo'"
        )


def test_flujo_completo_del_guion(client, superadmin, app):
    """GU-AT-01: recorrido de negocio de punta a punta."""
    nombre = f'Aceptacion {uuid.uuid4().hex[:6]}'

    # 1. Crear el guion desde la ruta real.
    creado = client.post('/guiones/crear', data={'nombre': nombre, 'tiempo_inning': '2,00'})
    assert creado.status_code == 302
    guion_id = int(creado.headers['Location'].rstrip('/').rsplit('/', 1)[1])

    # 2. Cargar dos pregame y dos game, como en la pantalla de elementos.
    elementos = [
        {'tipo': 'pregame', 'hora': '18:30', 'contenido': 'Himno nacional',
         'duracion_estimada': '1,30', 'encargado': 'Keiver'},
        {'tipo': 'pregame', 'hora': '18:45', 'contenido': 'Saludo del animador',
         'duracion_estimada': '1,00', 'encargado': 'Maria'},
        {'tipo': 'game', 'inning': '1', 'medio_inning': 'alta',
         'contenido': 'Promo del patrocinador', 'duracion_estimada': '2,00', 'encargado': 'Keiver'},
        {'tipo': 'game', 'inning': '1', 'medio_inning': 'baja',
         'contenido': 'Dinámica con el público', 'duracion_estimada': '1,30', 'encargado': 'Maria'},
    ]
    for datos in elementos:
        resp = client.post(f'/guiones/agregar-elemento/{guion_id}', data=datos)
        assert resp.status_code == 302

    secuencia = _elementos(guion_id)
    assert len(secuencia) == 4
    assert [e['tipo'] for e in secuencia] == ['pregame', 'pregame', 'game', 'game']

    # 3. Previsualizar: el operador ve los cuatro elementos.
    preview = client.get(f'/guiones/previsualizar/{guion_id}')
    html = preview.get_data(as_text=True)
    assert preview.status_code == 200
    assert 'Himno nacional' in html
    assert 'Dinámica con el público' in html

    # 4. Publicar: el guion queda listo para el show.
    assert client.post(f'/guiones/publicar/{guion_id}').status_code == 302
    from app.model.guion_model import GuionModel
    assert GuionModel().obtener_por_id(guion_id)['estado'] == 'publicado'

    # 5. Iniciar EN VIVO (cerrando cualquier show anterior de la suite).
    _cerrar_guiones_en_vivo()
    from app.model.en_vivo_model import EnVivoModel
    assert EnVivoModel().iniciar(guion_id) is True

    vista = client.get(f'/en-vivo/{guion_id}')
    assert vista.status_code == 200
    assert 'EN VIVO' in vista.get_data(as_text=True)

    estados = _estados(guion_id)
    activos = [eid for eid, estado in estados.items() if estado == 'en_curso']
    assert len(activos) == 1
    actual = activos[0]
    assert actual in [e['id'] for e in secuencia]

    # 6. Avanzar: completar el actual y poner en curso el siguiente.
    ids = [e['id'] for e in secuencia]
    siguiente = ids[ids.index(actual) + 1]
    client.post(f'/en-vivo/api/sincronizar/{guion_id}', json={'estados': [
        {'id': actual, 'estado': 'completado', 'accion': 'completar'},
        {'id': siguiente, 'estado': 'en_curso'},
    ]})
    estados = _estados(guion_id)
    assert estados[actual] == 'completado'
    assert estados[siguiente] == 'en_curso'

    # 7. Retroceder: el operador marcó mal y aún debe ejecutar el anterior.
    client.post(f'/en-vivo/api/sincronizar/{guion_id}', json={'estados': [
        {'id': actual, 'estado': 'en_curso', 'accion': 'reiniciar'},
        {'id': siguiente, 'estado': 'pendiente', 'accion': 'reiniciar'},
    ]})
    estados = _estados(guion_id)
    assert estados[actual] == 'en_curso'
    assert estados[siguiente] == 'pendiente'

    # 8. Finalizar: el show se cierra y se limpian los relojes.
    assert client.get(f'/en-vivo/finalizar/{guion_id}').status_code == 302
    assert client.get(f'/en-vivo/{guion_id}').status_code == 302

    db = _db()
    with db.cursor() as cur:
        cur.execute("SELECT estado, inicio_show FROM guiones WHERE id = %s", (guion_id,))
        cerrado = cur.fetchone()
        assert cerrado['estado'] == 'finalizado'
        assert cerrado['inicio_show'] is None

        cur.execute(
            "SELECT COUNT(*) t FROM elementos_guion "
            "WHERE guion_id = %s AND inicio_curso IS NOT NULL",
            (guion_id,),
        )
        assert cur.fetchone()['t'] == 0
