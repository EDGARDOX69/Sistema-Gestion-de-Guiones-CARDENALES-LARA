"""CP-GEN-UI-01: humo visual de las paginas principales de cada modulo."""

import pytest
from playwright.sync_api import expect

from soporte_ui import login

pytestmark = pytest.mark.ui

RUTAS = {
    'dashboard': '/dashboard',
    'guion': '/guiones/',
    'en_vivo': '/en-vivo/',
    'balance': '/balance/',
    'contratos': '/contratos/',
    'patrocinadores': '/patrocinador/',
    'premios': '/premio/',
    'inventario': '/inventario/',
    'mantenimiento': '/mantenimiento/',
    'tareas': '/gestion-tarea/',
    'reels': '/reels/',
    'usuarios': '/usuarios/',
    'roles': '/roles/',
    'reportes': '/reportes/',
    'bitacora': '/bitacora/',
}


def test_paginas_principales_cargan_sin_error(page, e2e_credenciales):
    login(page, e2e_credenciales)

    for modulo, ruta in RUTAS.items():
        respuesta = page.goto(ruta, wait_until='domcontentloaded')
        assert respuesta is not None, modulo
        assert respuesta.status == 200, f'{modulo}: {respuesta.status}'
        expect(page.locator('body')).to_be_visible()
        assert 'Error interno' not in page.content(), modulo


def test_paginas_principales_sin_desbordamiento_movil(page, e2e_credenciales):
    login(page, e2e_credenciales)
    page.set_viewport_size({'width': 390, 'height': 844})

    for modulo in ('dashboard', 'en_vivo', 'balance', 'usuarios'):
        page.goto(RUTAS[modulo], wait_until='domcontentloaded')
        desborda = page.evaluate(
            '() => document.documentElement.scrollWidth > window.innerWidth'
        )
        assert not desborda, modulo
