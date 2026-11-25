"""GU-UI — Pruebas de interfaz del módulo guion con Playwright.

Se ejecutan contra un servidor propio levantado por `conftest.py` y contra
``estadio_db_test`` y ``seguridad_test``. El usuario E2E se crea antes de
arrancar el servidor, así que no dependen de credenciales del `.env`:

    E2E=1 pytest test/interfaz -m ui
"""
import re
import uuid

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


def _login(page: Page, credenciales) -> None:
    """Login real; rellena el CAPTCHA solo si la bandera lo deja visible."""
    page.goto('/auth/login')
    if page.locator('#captcha_text').count():
        tiles = page.locator('.captcha-tile')
        expect(tiles).to_have_count(4)
        codigo = ''.join(texto.strip() for texto in tiles.all_text_contents())
        page.fill('#captcha_text', codigo)

    page.fill('#email', credenciales['email'])
    page.fill('#password', credenciales['password'])
    page.click('#btnLogin')
    page.wait_for_url(re.compile(r'/dashboard'), timeout=30_000)


def _crear_guion_por_ui(page: Page) -> tuple[str, int]:
    """Crea un guion desde el formulario y devuelve (nombre, id)."""
    nombre = f'UI {uuid.uuid4().hex[:6]}'
    page.goto('/guiones/crear')
    page.fill('#nombre', nombre)
    page.fill('#tiempo_inning', '2,00')
    page.get_by_role('button', name=re.compile(r'Crear Gui[oó]n', re.I)).click()
    # el formulario confirma con SweetAlert antes de enviar
    page.get_by_role('button', name=re.compile(r'S[ií], crear', re.I)).click()
    page.wait_for_url(re.compile(r'/guiones/agregar-elemento/\d+'), timeout=15_000)

    guion_id = int(page.url.rstrip('/').rsplit('/', 1)[1])
    return nombre, guion_id


def test_dashboard_de_guiones_carga(page: Page, e2e_credenciales):
    """GU-UI-01: un operador autenticado ve la gestión de guiones."""
    _login(page, e2e_credenciales)
    page.goto('/guiones/')
    expect(page.get_by_role('heading', name=re.compile(r'Gesti[oó]n de Guiones', re.I))).to_be_visible()
    expect(page.get_by_role('link', name=re.compile(r'Nuevo Gui[oó]n', re.I))).to_be_visible()


def test_formulario_de_creacion_tiene_sus_campos(page: Page, e2e_credenciales):
    """GU-UI-02: nombre y tiempo de inning están disponibles."""
    _login(page, e2e_credenciales)
    page.goto('/guiones/crear')
    expect(page.locator('#nombre')).to_be_visible()
    expect(page.locator('#tiempo_inning')).to_be_visible()
    expect(page.get_by_role('button', name=re.compile(r'Crear Gui[oó]n', re.I))).to_be_visible()


def test_crear_guion_desde_la_interfaz(page: Page, e2e_credenciales):
    """GU-UI-03: el formulario crea el guion y lleva a agregar elementos."""
    _login(page, e2e_credenciales)
    nombre, guion_id = _crear_guion_por_ui(page)

    expect(page.locator('#tipoSelect')).to_be_visible()
    expect(page.locator('#contenido')).to_be_visible()
    assert nombre in page.content()

    # limpieza: borrado lógico del guion creado por la prueba
    page.goto(f'/guiones/eliminar/{guion_id}')
    page.wait_for_url(re.compile(r'/guiones/$'), timeout=15_000)
    expect(page.get_by_role('heading', name=re.compile(r'Gesti[oó]n de Guiones', re.I))).to_be_visible()


def test_previsualizar_un_guion_creado(page: Page, e2e_credenciales):
    """GU-UI-04: la vista previa se abre desde la UI."""
    _login(page, e2e_credenciales)
    nombre, guion_id = _crear_guion_por_ui(page)

    page.goto(f'/guiones/previsualizar/{guion_id}')
    expect(page.locator('body')).to_contain_text(nombre.split(' - ')[0])
    expect(page.get_by_role('link', name=re.compile(r'Volver', re.I))).to_be_visible()

    page.goto(f'/guiones/eliminar/{guion_id}')
    page.wait_for_url(re.compile(r'/guiones/$'), timeout=15_000)
