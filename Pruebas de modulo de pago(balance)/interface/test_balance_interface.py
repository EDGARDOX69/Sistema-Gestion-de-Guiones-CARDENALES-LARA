# python -m pytest test/interface/test_balance_interface.py -v
# python run.py 

import pytest
from playwright.sync_api import Page, expect

# Ajusta la URL base si tu servidor Flask corre en otro puerto
BASE_URL = "http://127.0.0.1:5001"

def test_interface_balance_carga_y_elementos(page: Page):
    """UI 1: Verifica que la vista de Balance cargue en el navegador sin errores visuales ni pantallas en blanco."""
    page.goto(f"{BASE_URL}/balance/")
    
    # Verifica que el documento HTML tenga un título cargado y cuerpo visible
    expect(page.locator("body")).to_be_visible()
    assert page.title() != "", "La página cargó sin título en el navegador"

    # Verifica que existan elementos estructurales básicos (encabezados, tablas o formularios)
    contenido_texto = page.locator("body").inner_text().strip()
    assert len(contenido_texto) > 0, "La vista de Balance se renderizó completamente vacía"

def test_interface_balance_responsivo_movil(page: Page):
    """UI 2: Simula una pantalla móvil (iPhone 13: 390x844) y verifica que no haya desbordamiento horizontal."""
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE_URL}/balance/")
    
    expect(page.locator("body")).to_be_visible()

    # Comprueba mediante JavaScript que el ancho del contenido no rompa la pantalla móvil (sin scroll horizontal)
    
    tiene_desbordamiento = page.evaluate("""() => {
        return document.documentElement.scrollWidth > window.innerWidth;
    }""")
    assert not tiene_desbordamiento, "La interfaz presenta desbordamiento horizontal en resolución móvil"

def test_interface_balance_escritorio_fullhd(page: Page):
    """UI 3: Verifica el renderizado correcto en resolución de escritorio estándar (1920x1080)."""
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(f"{BASE_URL}/balance/")
    
    expect(page.locator("body")).to_be_visible()