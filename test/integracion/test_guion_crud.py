"""GU-IT — Pruebas de integración del módulo guion (Flask + MySQL de prueba).

Corren contra `estadio_db_test` / `seguridad_test`, clonadas por
`test/conftest.py`. Nunca tocan las bases reales.

Qué se prueba y por qué:
- `GuionModel.registrar`: la escritura es compuesta (guion + fecha). Si la
  transacción se rompe, quedaría un guion sin fecha.
- `eliminar`: debe ser borrado lógico (`status = 0`), no físico.
- `replicar`: copia cabecera, fechas y elementos a cada fecha destino.
- `ElementoGuionModel`: orden, ocupados, último orden y ordenamiento final son
  las reglas que sostienen la vista previa y EN VIVO.
"""
from datetime import date, time

import pytest

from app.model.guion_model import ElementoGuionModel, GuionModel

pytestmark = [pytest.mark.integration, pytest.mark.db]


def _elemento(guion_id, *, tipo='pregame', contenido='Himno nacional',
              hora=time(18, 30), inning=None, medio=None, orden=1,
              duracion=60, encargado='Keiver'):
    modelo = ElementoGuionModel()
    modelo.set_guion_id(guion_id)
    modelo.set_tipo(tipo)
    modelo.set_contenido(contenido)
    modelo.set_hora(hora)
    modelo.set_inning(inning)
    modelo.set_medio_inning(medio)
    modelo.set_duracion_estimada(duracion)
    modelo.set_encargado(encargado)
    modelo.set_orden(orden)
    return modelo


# ---------------------------------------------------------------------------
# GU-IT-01 .. GU-IT-07 — cabecera del guion
# ---------------------------------------------------------------------------

def test_registrar_crea_guion_y_fecha_en_una_transaccion(app):
    """GU-IT-01: el guion y su fecha nacen juntos."""
    modelo = GuionModel()
    guion_id = modelo.registrar({
        'nombre': 'Guion Integración',
        'fecha': date(2026, 12, 1),
        'tiempo_inning': 5400,
    })

    assert guion_id is not None
    guardado = modelo.obtener_por_id(guion_id)
    assert guardado['nombre'] == 'Guion Integración'
    assert guardado['estado'] == 'borrador'
    assert guardado['status'] == 1
    assert guardado['tiempo_inning'] == 5400

    fechas = modelo.obtener_fechas(guion_id)
    assert len(fechas) == 1
    assert fechas[0]['fecha'] == date(2026, 12, 1)


@pytest.mark.parametrize('datos', [
    {'nombre': '', 'fecha': date(2026, 1, 1)},
    {'nombre': 'ab', 'fecha': date(2026, 1, 1)},
    {'nombre': 'x' * 51, 'fecha': date(2026, 1, 1)},
    {'nombre': 'Sin fecha', 'fecha': None},
])
def test_registrar_invalido_no_escribe_nada(app, datos):
    """GU-IT-02: si la validación falla, no hay INSERT (ni guion ni fecha)."""
    nombre = datos['nombre']
    modelo = GuionModel()
    assert modelo.registrar(datos) is None
    if nombre:
        with app.app_context():
            from app.database import Database
            db = Database.get_connection('estadio_db')
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) t FROM guiones WHERE nombre = %s", (nombre,)
                )
                assert cur.fetchone()['t'] == 0


def test_consultar_excluye_eliminados(app, crear_guion):
    """GU-IT-03: `consultar` solo devuelve status = 1."""
    modelo = GuionModel()
    guion_id = crear_guion(nombre='Guion Visible')
    assert any(g['id'] == guion_id for g in modelo.consultar())

    assert modelo.eliminar(guion_id) is True
    assert all(g['id'] != guion_id for g in modelo.consultar())


def test_eliminar_es_borrado_logico(app, crear_guion):
    """GU-IT-04: el registro sigue en la tabla, marcado con status = 0."""
    guion_id = crear_guion(nombre='Guion Borrado')
    assert GuionModel().eliminar(guion_id) is True

    from app.database import Database
    db = Database.get_connection('estadio_db')
    with db.cursor() as cur:
        cur.execute("SELECT status FROM guiones WHERE id = %s", (guion_id,))
        assert cur.fetchone()['status'] == 0
    assert GuionModel().obtener_por_id(guion_id) is None


def test_modificar_nombre_y_estado(app, crear_guion):
    """GU-IT-05: modificar devuelve el registro actualizado."""
    guion_id = crear_guion(nombre='Guion Original')
    modelo = GuionModel()
    actualizado = modelo.modificar(guion_id, {'nombre': 'Guion Editado', 'estado': 'publicado'})

    assert actualizado['nombre'] == 'Guion Editado'
    assert actualizado['estado'] == 'publicado'
    assert actualizado['modificado_en'] is not None


def test_modificar_fechas_reemplaza_el_conjunto(app, crear_guion):
    """GU-IT-06: enviar `fechas` reemplaza todas las anteriores."""
    guion_id = crear_guion(nombre='Guion Fechas')
    modelo = GuionModel()
    modelo.modificar(guion_id, {'fechas': [date(2026, 12, 1), date(2026, 12, 2)]})
    assert len(modelo.obtener_fechas(guion_id)) == 2

    modelo.modificar(guion_id, {'fechas': [date(2027, 1, 5)]})
    fechas = modelo.obtener_fechas(guion_id)
    assert len(fechas) == 1
    assert fechas[0]['fecha'] == date(2027, 1, 5)


def test_verificar_nombre_detecta_la_base(app):
    """GU-IT-07: la UI comprueba duplicados por el nombre base (sin la fecha)."""
    modelo = GuionModel()
    modelo.registrar({'nombre': 'Show Viernes - 2026-12-01', 'fecha': date(2026, 12, 1)})

    assert modelo.verificar_nombre('Show Viernes') is True
    assert modelo.verificar_nombre('Show Sabado') is False


# ---------------------------------------------------------------------------
# GU-IT-08 .. GU-IT-10 — replicar
# ---------------------------------------------------------------------------

def test_replicar_copia_elementos_en_cada_fecha(app, crear_guion):
    """GU-IT-08: replicar crea un guion por fecha con todos sus elementos."""
    origen_id = crear_guion(nombre='Guion Origen')
    assert _elemento(origen_id, orden=1).confirmar_registro()
    assert _elemento(
        origen_id, tipo='game', contenido='Promo especial', hora=None,
        inning=1, medio='alta', orden=2,
    ).confirmar_registro()

    destino = [date(2026, 12, 5), date(2026, 12, 6)]
    ids = GuionModel().replicar(origen_id, destino, 'Guion Base')

    assert len(ids) == 2
    modelo = GuionModel()
    elem_model = ElementoGuionModel()
    for guion_id, fecha in zip(ids, destino):
        cabecera = modelo.obtener_por_id(guion_id)
        assert cabecera['estado'] == 'borrador'
        assert cabecera['nombre'] == f'Guion Base - {fecha}'
        assert [f['fecha'] for f in modelo.obtener_fechas(guion_id)] == [fecha]
        assert len(elem_model.consultar(guion_id=guion_id)) == 2


def test_replicar_guion_inexistente_devuelve_lista_vacia(app):
    """GU-IT-09: no se inventa nada si el origen no existe."""
    assert GuionModel().replicar(99999999, [date(2026, 12, 1)], 'Base') == []


def test_replicar_no_toca_el_origen(app, crear_guion):
    """GU-IT-10: el guion original conserva sus datos y elementos."""
    origen_id = crear_guion(nombre='Guion Intacto')
    _elemento(origen_id, orden=1).confirmar_registro()

    GuionModel().replicar(origen_id, [date(2026, 12, 7)], 'Copia')

    assert GuionModel().obtener_por_id(origen_id)['nombre'] == 'Guion Intacto'
    assert len(ElementoGuionModel().consultar(guion_id=origen_id)) == 1


# ---------------------------------------------------------------------------
# GU-IT-11 .. GU-IT-18 — elementos
# ---------------------------------------------------------------------------

def test_elemento_pregame_se_registra_y_se_lee(app, crear_guion):
    """GU-IT-11: alta de un pregame con su orden y duración."""
    guion_id = crear_guion()
    guardado = _elemento(
        guion_id, contenido='Himno nacional', hora=time(18, 30), duracion=90, orden=1,
    ).confirmar_registro()

    assert guardado is not None
    assert guardado['tipo'] == 'pregame'
    assert guardado['contenido'] == 'Himno nacional'
    assert guardado['duracion_estimada'] == 90
    assert guardado['orden'] == 1


def test_elemento_game_se_registra_con_inning(app, crear_guion):
    """GU-IT-12: alta de un game con inning y mitad."""
    guion_id = crear_guion()
    guardado = _elemento(
        guion_id, tipo='game', contenido='Promo especial', hora=None,
        inning=1, medio='alta', orden=2,
    ).confirmar_registro()

    assert guardado['tipo'] == 'game'
    assert guardado['inning'] == 1
    assert guardado['medio_inning'] == 'alta'


def test_elemento_game_sin_inning_no_se_registra(app, crear_guion):
    """GU-IT-13: la validación del modelo frena el INSERT."""
    guion_id = crear_guion()
    assert _elemento(
        guion_id, tipo='game', contenido='Promo especial', hora=None,
        inning=None, medio='alta', orden=1,
    ).confirmar_registro() is None
    assert len(ElementoGuionModel().consultar(guion_id=guion_id)) == 0


def test_consultar_respeta_el_orden(app, crear_guion):
    """GU-IT-14: `consultar` ordena por orden ascendente."""
    guion_id = crear_guion()
    _elemento(guion_id, contenido='Tercero', hora=time(20, 0), orden=3).confirmar_registro()
    _elemento(guion_id, contenido='Primero', hora=time(18, 0), orden=1).confirmar_registro()
    _elemento(guion_id, contenido='Segundo', hora=time(19, 0), orden=2).confirmar_registro()

    elementos = ElementoGuionModel().consultar(guion_id=guion_id)
    assert [e['contenido'] for e in elementos] == ['Primero', 'Segundo', 'Tercero']


def test_obtener_ocupados_devuelve_horas_e_innings(app, crear_guion):
    """GU-IT-15: la UI usa esto para bloquear choques de horario."""
    guion_id = crear_guion()
    pregame = _elemento(guion_id, hora=time(18, 30), orden=1).confirmar_registro()
    game = _elemento(
        guion_id, tipo='game', contenido='Promo', hora=None,
        inning=1, medio='alta', orden=2,
    ).confirmar_registro()

    horas, innings = ElementoGuionModel().obtener_ocupados(guion_id)
    assert horas == {'18:30'}
    assert innings == {'1-alta': game['id']}
    assert pregame['id'] not in innings.values()


def test_obtener_ultimo_orden_por_tipo(app, crear_guion):
    """GU-IT-16: el siguiente elemento continúa la numeración de su tipo."""
    guion_id = crear_guion()
    _elemento(guion_id, orden=1).confirmar_registro()
    _elemento(guion_id, contenido='Segundo pregame', hora=time(19, 0), orden=2).confirmar_registro()
    _elemento(
        guion_id, tipo='game', contenido='Promo', hora=None,
        inning=1, medio='alta', orden=1,
    ).confirmar_registro()

    modelo = ElementoGuionModel()
    assert modelo.obtener_ultimo_orden(guion_id, 'pregame') == 2
    assert modelo.obtener_ultimo_orden(guion_id, 'game') == 1


def test_consultar_excepto_excluye_el_editado(app, crear_guion):
    """GU-IT-17: al editar no debe chocar consigo mismo."""
    guion_id = crear_guion()
    primero = _elemento(guion_id, orden=1).confirmar_registro()
    segundo = _elemento(guion_id, contenido='Segundo', hora=time(19, 0), orden=2).confirmar_registro()

    otros = ElementoGuionModel().consultar_excepto(guion_id, primero['id'])
    assert [e['id'] for e in otros] == [segundo['id']]


def test_ordenamiento_de_preview_pregame_por_hora_y_game_por_inning(app, crear_guion):
    """GU-IT-18: previsualización y EN VIVO comparten este orden."""
    guion_id = crear_guion()
    _elemento(guion_id, contenido='Pregame tarde', hora=time(19, 30), orden=1).confirmar_registro()
    _elemento(guion_id, contenido='Pregame temprano', hora=time(18, 15), orden=2).confirmar_registro()
    _elemento(
        guion_id, tipo='game', contenido='Game 2 baja', hora=None,
        inning=2, medio='baja', orden=3,
    ).confirmar_registro()
    _elemento(
        guion_id, tipo='game', contenido='Game 1 alta', hora=None,
        inning=1, medio='alta', orden=4,
    ).confirmar_registro()

    pregame, game = ElementoGuionModel().obtener_por_guion_ordenados(guion_id)
    assert [e['contenido'] for e in pregame] == ['Pregame temprano', 'Pregame tarde']
    assert [e['contenido'] for e in game] == ['Game 1 alta', 'Game 2 baja']


def test_modificar_y_eliminar_elemento(app, crear_guion):
    """GU-IT-19: editar conserva el id; eliminar sí borra la fila."""
    guion_id = crear_guion()
    elemento = _elemento(guion_id, contenido='Texto original', orden=1).confirmar_registro()
    modelo = ElementoGuionModel()

    actualizado = modelo.modificar(elemento['id'], {'contenido': 'Texto corregido'})
    assert actualizado['id'] == elemento['id']
    assert actualizado['contenido'] == 'Texto corregido'

    modelo.eliminar(elemento['id'])
    assert modelo.obtener_por_id(elemento['id']) is None
