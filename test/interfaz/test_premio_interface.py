# python -m pytest test/interface/test_premio_interface.py -v
# python run.py

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5001"

def test_interface_premio_escritorio_y_elementos_clave(page: Page):
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{BASE_URL}/premio/")

    expect(page.locator("#kpi-pendientes")).to_be_visible()
    expect(page.locator("#kpi-entregados")).to_be_visible()
    expect(page.locator("#pos-buscador")).to_be_visible()
    expect(page.locator("#contenedor-catalogo")).to_be_visible()

    # Verificar apertura del modal de registro al hacer clic en Nuevo Premio
    page.locator("#btnNuevoPremio").click()
    expect(page.locator("#modalPremio")).to_be_visible()


def test_interface_premio_responsivo_movil(page: Page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE_URL}/premio/")

    tiene_desbordamiento = page.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth"
    )
    assert not tiene_desbordamiento, "Desbordamiento horizontal detectado en móvil"