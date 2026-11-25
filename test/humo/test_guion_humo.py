"""GU-SM — Pruebas de humo del módulo guion.

Objetivo: en pocos segundos, confirmar que el módulo "está de pie": las rutas
responden, el formulario de creación funciona y ninguna vista lanza un 500.
No sustituyen a las de integración: son el primer filtro antes de una demo.
"""
import uuid

import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.db]


def test_dashboard_responde(client, superadmin):
    """GU-SM-01: la pantalla principal del módulo carga."""
    resp = client.get('/guiones/')
    assert resp.status_code == 200
    assert 'Gestión de Guiones' in resp.get_data(as_text=True)


def test_crear_guion_minimo(client, superadmin):
    """GU-SM-02: el flujo mínimo crear guion -> agregar elementos."""
    resp = client.post(
        '/guiones/crear',
        data={'nombre': f'Humo {uuid.uuid4().hex[:6]}'},
    )
    assert resp.status_code == 302
    assert '/guiones/agregar-elemento/' in resp.headers['Location']


def test_rutas_del_modulo_no_devuelven_500(client, superadmin, crear_guion):
    """GU-SM-03: recorrido de todas las vistas con un guion real."""
    guion_id = crear_guion(nombre='Guion Humo')

    rutas = [
        '/guiones/',
        '/guiones/crear',
        f'/guiones/agregar-elemento/{guion_id}',
        f'/guiones/editar/{guion_id}',
        f'/guiones/previsualizar/{guion_id}',
        f'/guiones/publicar/{guion_id}',
        f'/guiones/replicar/{guion_id}',
    ]
    for ruta in rutas:
        resp = client.get(ruta)
        assert resp.status_code in (200, 302), f'{ruta} respondió {resp.status_code}'
        assert resp.status_code != 500, f'{ruta} explotó'


def test_guion_inexistente_redirige(client, superadmin):
    """GU-SM-04: un id inexistente no rompe la vista, redirige."""
    for ruta in ('/guiones/editar/99999999', '/guiones/previsualizar/99999999'):
        resp = client.get(ruta)
        assert resp.status_code == 302
        assert '/guiones/' in resp.headers['Location']
