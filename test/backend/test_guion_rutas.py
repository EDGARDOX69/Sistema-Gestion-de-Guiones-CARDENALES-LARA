"""GU-API — Pruebas de las rutas HTTP del módulo guion.

Qué se prueba y por qué:
- Permisos: sin sesión y sin permiso no se entra; con Superadmin sí.
- Validación de servidor: los POST inválidos no deben escribir en la BD,
  aunque el navegador permita enviarlos.
- Contrato JSON de `/guiones/verificar-nombre`, que consume el JS.
- Efectos reales: publicar, eliminar (lógico), replicar y bitácora.
"""
import uuid
from datetime import date

import pytest

pytestmark = [pytest.mark.api, pytest.mark.db]


def _db(esquema='estadio_db'):
    from app.database import Database
    return Database.get_connection(esquema)


def _contar_guiones():
    db = _db()
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) t FROM guiones WHERE status = 1")
        return cur.fetchone()['t']


def _elementos(guion_id):
    from app.model.guion_model import ElementoGuionModel
    return ElementoGuionModel().consultar(guion_id=guion_id)


def _elemento(guion_id, *, tipo='pregame', contenido='Himno nacional',
              hora='18:30', inning=None, medio=None, orden=1):
    from app.model.guion_model import ElementoGuionModel
    from datetime import time
    modelo = ElementoGuionModel()
    modelo.set_guion_id(guion_id)
    modelo.set_tipo(tipo)
    modelo.set_contenido(contenido)
    modelo.set_hora(time.fromisoformat(hora) if hora else None)
    modelo.set_inning(inning)
    modelo.set_medio_inning(medio)
    modelo.set_duracion_estimada(60)
    modelo.set_encargado('Keiver')
    modelo.set_orden(orden)
    return modelo.confirmar_registro()


# ---------------------------------------------------------------------------
# GU-API-01 .. GU-API-04 — acceso
# ---------------------------------------------------------------------------

def test_anonimo_redirige_al_login(client):
    """GU-API-01: el módulo no es público."""
    resp = client.get('/guiones/')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_usuario_sin_permiso_es_rechazado(client, crear_usuario, login):
    """GU-API-02: rol sin permisos de guion vuelve al dashboard."""
    usuario = crear_usuario(rol='SinPermisos')
    login(usuario)

    resp = client.get('/guiones/')
    assert resp.status_code == 302
    assert '/dashboard' in resp.headers['Location']


def test_superadmin_entra_al_dashboard(client, superadmin):
    """GU-API-03: con `guion.view` la vista responde 200."""
    resp = client.get('/guiones/')
    assert resp.status_code == 200
    assert 'Gestión de Guiones' in resp.get_data(as_text=True)


def test_post_sin_permiso_no_escribe(client, crear_usuario, login):
    """GU-API-04: el permiso se exige también en escrituras (POST -> 403)."""
    usuario = crear_usuario(rol='SinPermisos')
    login(usuario)
    antes = _contar_guiones()

    resp = client.post('/guiones/crear', data={'nombre': f'Intruso {uuid.uuid4().hex[:6]}'})
    assert resp.status_code == 403
    assert _contar_guiones() == antes


# ---------------------------------------------------------------------------
# GU-API-05 .. GU-API-08 — crear guion
# ---------------------------------------------------------------------------

def test_crear_guion_agrega_la_fecha_al_nombre(client, superadmin):
    """GU-API-05: el controlador compone "nombre - YYYY-MM-DD"."""
    nombre = f'API Crear {uuid.uuid4().hex[:6]}'
    resp = client.post('/guiones/crear', data={'nombre': nombre, 'tiempo_inning': '1,30'})

    assert resp.status_code == 302
    assert '/guiones/agregar-elemento/' in resp.headers['Location']
    guion_id = int(resp.headers['Location'].rstrip('/').rsplit('/', 1)[1])

    db = _db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM guiones WHERE id = %s", (guion_id,))
        fila = cur.fetchone()
    assert fila['nombre'] == f'{nombre} - {date.today()}'
    assert fila['estado'] == 'borrador'
    assert fila['tiempo_inning'] == 90


@pytest.mark.parametrize('nombre', ['ab', '', '   '])
def test_crear_guion_con_nombre_base_invalido_no_deberia_escribir(client, superadmin, nombre):
    """GU-API-06: el servidor rechaza el nombre base antes de concatenar la fecha."""
    antes = _contar_guiones()
    resp = client.post('/guiones/crear', data={'nombre': nombre})

    assert resp.status_code == 200          # debería volver al formulario
    assert _contar_guiones() == antes       # y no escribir nada


def test_crear_guion_con_nombre_demasiado_largo_no_escribe(app, client, superadmin):
    """GU-API-07: el modelo sí rechaza el nombre compuesto que pasa de 50."""
    antes = _contar_guiones()
    resp = client.post('/guiones/crear', data={'nombre': 'x' * 60})

    assert resp.status_code == 200
    assert _contar_guiones() == antes


def test_crear_guion_redirige_a_agregar_elementos(client, superadmin):
    """GU-API-08: el flujo natural continúa en la pantalla de elementos."""
    resp = client.post(
        '/guiones/crear',
        data={'nombre': f'API Flujo {uuid.uuid4().hex[:6]}'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    destino = resp.headers['Location']
    assert '/guiones/agregar-elemento/' in destino

    pagina = client.get(destino)
    assert pagina.status_code == 200
    assert 'Agregar Elemento' in pagina.get_data(as_text=True)


# ---------------------------------------------------------------------------
# GU-API-09 .. GU-API-11 — verificar nombre
# ---------------------------------------------------------------------------

def test_verificar_nombre_detecta_duplicado(client, superadmin, crear_guion):
    """GU-API-09: el JS avisa antes de crear un duplicado."""
    base = f'Duplicado {uuid.uuid4().hex[:6]}'
    crear_guion(nombre=f'{base} - 2099-01-01')

    resp = client.post('/guiones/verificar-nombre', data={'nombre': base})
    assert resp.status_code == 200
    assert resp.get_json() == {'existe': True}


def test_verificar_nombre_libre_responde_false(client, superadmin):
    """GU-API-10: un nombre nuevo no bloquea el formulario."""
    resp = client.post(
        '/guiones/verificar-nombre',
        data={'nombre': f'Libre {uuid.uuid4().hex[:8]}'},
    )
    assert resp.get_json() == {'existe': False}


def test_verificar_nombre_vacio_responde_false(client, superadmin):
    """GU-API-11: campo vacío no consulta la BD ni rompe el JSON."""
    resp = client.post('/guiones/verificar-nombre', data={'nombre': ''})
    assert resp.get_json() == {'existe': False}


# ---------------------------------------------------------------------------
# GU-API-12 .. GU-API-17 — elementos
# ---------------------------------------------------------------------------

def test_agregar_pregame_por_post(client, superadmin, crear_guion):
    """GU-API-12: alta de pregame y conversión de duración."""
    guion_id = crear_guion()
    resp = client.post(f'/guiones/agregar-elemento/{guion_id}', data={
        'tipo': 'pregame',
        'hora': '18:30',
        'contenido': 'Himno nacional',
        'duracion_estimada': '90',
        'encargado': 'Keiver',
    })

    assert resp.status_code == 302
    elementos = _elementos(guion_id)
    assert len(elementos) == 1
    assert elementos[0]['contenido'] == 'Himno nacional'
    assert elementos[0]['duracion_estimada'] == 5400   # "90" se lee como minutos


def test_agregar_pregame_con_hora_ocupada_rechazado(client, superadmin, crear_guion):
    """GU-API-13: no se pisan dos pregame a la misma hora."""
    guion_id = crear_guion()
    datos = {
        'tipo': 'pregame',
        'hora': '18:30',
        'contenido': 'Himno nacional',
        'duracion_estimada': '1,30',
        'encargado': 'Keiver',
    }
    client.post(f'/guiones/agregar-elemento/{guion_id}', data=datos)

    resp = client.post(
        f'/guiones/agregar-elemento/{guion_id}',
        data={**datos, 'contenido': 'Otro pregame'},
        follow_redirects=True,
    )
    assert 'Esa hora ya esta ocupada' in resp.get_data(as_text=True)
    assert len(_elementos(guion_id)) == 1


def test_agregar_game_sin_inning_rechazado(client, superadmin, crear_guion):
    """GU-API-14: el game exige inning y medio."""
    guion_id = crear_guion()
    resp = client.post(
        f'/guiones/agregar-elemento/{guion_id}',
        data={
            'tipo': 'game',
            'inning': '',
            'medio_inning': 'alta',
            'contenido': 'Promo especial',
            'duracion_estimada': '1,00',
            'encargado': 'Keiver',
        },
        follow_redirects=True,
    )

    assert 'Para Game debes seleccionar inning y medio' in resp.get_data(as_text=True)
    assert len(_elementos(guion_id)) == 0


def test_agregar_tipo_invalido_rechazado(client, superadmin, crear_guion):
    """GU-API-15: el enum pregame/game se valida en el controlador."""
    guion_id = crear_guion()
    resp = client.post(
        f'/guiones/agregar-elemento/{guion_id}',
        data={'tipo': 'hackeado', 'contenido': 'Contenido válido', 'encargado': 'Keiver'},
        follow_redirects=True,
    )

    assert 'Tipo de elemento inválido' in resp.get_data(as_text=True)
    assert len(_elementos(guion_id)) == 0


def test_editar_elemento_actualiza_contenido(client, superadmin, crear_guion):
    """GU-API-16: la edición conserva el elemento y cambia sus datos."""
    guion_id = crear_guion()
    elemento = _elemento(guion_id, contenido='Texto original')

    resp = client.post(
        f'/guiones/editar-elemento/{guion_id}/{elemento["id"]}',
        data={
            'tipo': 'pregame',
            'hora': '18:30',
            'contenido': 'Texto corregido',
            'duracion_estimada': '2,00',
            'encargado': 'Maria',
        },
    )

    assert resp.status_code == 302
    from app.model.guion_model import ElementoGuionModel
    actualizado = ElementoGuionModel().obtener_por_id(elemento['id'])
    assert actualizado['contenido'] == 'Texto corregido'
    assert actualizado['encargado'] == 'Maria'


def test_eliminar_elemento_lo_borra_de_la_tabla(client, superadmin, crear_guion):
    """GU-API-17: los elementos sí se eliminan físicamente."""
    guion_id = crear_guion()
    elemento = _elemento(guion_id)

    resp = client.get(f'/guiones/eliminar-elemento/{guion_id}/{elemento["id"]}')
    assert resp.status_code == 302

    from app.model.guion_model import ElementoGuionModel
    assert ElementoGuionModel().obtener_por_id(elemento['id']) is None


# ---------------------------------------------------------------------------
# GU-API-18 .. GU-API-22 — resto del ciclo de vida
# ---------------------------------------------------------------------------

def test_previsualizar_muestra_los_elementos(client, superadmin, crear_guion):
    """GU-API-18: la vista previa responde y pinta el contenido."""
    guion_id = crear_guion(nombre='Guion Preview')
    _elemento(guion_id, contenido='Himno nacional')

    resp = client.get(f'/guiones/previsualizar/{guion_id}')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert 'Himno nacional' in html
    assert 'Guion Preview' in html


def test_publicar_cambia_el_estado(client, superadmin, crear_guion):
    """GU-API-19: publicar deja el guion listo para EN VIVO."""
    guion_id = crear_guion(nombre='Guion Publicar')

    assert client.get(f'/guiones/publicar/{guion_id}').status_code == 200
    resp = client.post(f'/guiones/publicar/{guion_id}')
    assert resp.status_code == 302

    from app.model.guion_model import GuionModel
    assert GuionModel().obtener_por_id(guion_id)['estado'] == 'publicado'


def test_eliminar_guion_es_borrado_logico(client, superadmin, crear_guion):
    """GU-API-20: eliminar no destruye el histórico."""
    guion_id = crear_guion(nombre='Guion Eliminar')

    resp = client.get(f'/guiones/eliminar/{guion_id}')
    assert resp.status_code == 302

    db = _db()
    with db.cursor() as cur:
        cur.execute("SELECT status FROM guiones WHERE id = %s", (guion_id,))
        assert cur.fetchone()['status'] == 0


def test_replicar_por_post_crea_un_guion_por_fecha(client, superadmin, crear_guion):
    """GU-API-21: replicar acepta una lista CSV de fechas."""
    origen_id = crear_guion(nombre='Guion Replicar')
    _elemento(origen_id, contenido='Elemento replicado')

    resp = client.post(f'/guiones/replicar/{origen_id}', data={
        'nombre_base': 'Replica API',
        'fechas': '2026-12-01,2026-12-02',
    })
    assert resp.status_code == 302

    db = _db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT id, nombre FROM guiones WHERE nombre LIKE 'Replica API - %' AND status = 1"
        )
        creados = cur.fetchall()
    assert len(creados) == 2
    assert {c['nombre'] for c in creados} == {
        'Replica API - 2026-12-01', 'Replica API - 2026-12-02',
    }


def test_bitacora_registra_la_creacion(client, superadmin, app):
    """GU-API-22: una escritura deja rastro en seguridad.actividad_usuario."""
    client.post('/guiones/crear', data={'nombre': f'Bitacora {uuid.uuid4().hex[:6]}'})

    db = _db('seguridad')
    with db.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) t FROM actividad_usuario "
            "WHERE usuario_id = %s AND modulo = 'guion' AND accion = 'Crear guion'",
            (superadmin.id,),
        )
        assert cur.fetchone()['t'] >= 1
