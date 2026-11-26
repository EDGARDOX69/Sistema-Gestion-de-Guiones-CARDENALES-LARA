import os
import re
import pytest
from playwright.sync_api import Page, expect

def iniciar_sesion_si_es_necesario(page: Page):
    """Función auxiliar para hacer login rápido si el sistema redirige al login."""
    if "/auth/login" in page.url:
        email = os.getenv("E2E_EMAIL")
        password = os.getenv("E2E_PASSWORD")
        if not email or not password:
            pytest.fail("Define E2E_EMAIL y E2E_PASSWORD con las credenciales de prueba.")

        page.fill("input[name='email']", email)
        page.fill("input[name='password']", password)
        print("Completa el CAPTCHA en el navegador para continuar.")
        page.wait_for_function(
            "() => document.querySelector('#captcha_text')?.value.trim().length === 4",
            timeout=120_000,
        )
        page.click("button[type='submit'], input[type='submit']")
        page.wait_for_load_state("networkidle")
        if "/auth/login" in page.url:
            pytest.fail("No se pudo iniciar sesión. Verifica las credenciales y el CAPTCHA.")

def test_smoke_dashboard_inventario(page: Page):
    """
    Prueba de humo: Verifica que la ruta principal del inventario responde
    y carga el dashboard correctamente.
    """
    page.goto("http://127.0.0.1:5001/inventario/")
    
    iniciar_sesion_si_es_necesario(page)

    expect(page).to_have_url(re.compile(r".*/inventario/?$"))
    
    header = page.locator("h1, h2, .card-title").filter(has_text=re.compile(r"inventario|activos", re.IGNORECASE))
    if header.count() > 0:
        expect(header.first).to_be_visible()

def test_flujo_crear_recurso(page: Page):
    """
    Prueba de interfaz: Simula el registro de un nuevo recurso
    a través del formulario en /inventario/crear.
    """
    page.goto("http://127.0.0.1:5001/inventario/crear")
    
    iniciar_sesion_si_es_necesario(page)
    
    if not "/inventario/crear" in page.url:
        page.goto("http://127.0.0.1:5001/inventario/crear")

    page.fill("input[name='nombre']", "Monitor Dell 24 Test")
    page.fill("textarea[name='descripcion']", "Monitor de prueba automatizada con Playwright")
    
    tipo_select = page.locator("select[name='tipo_id']")
    if tipo_select.count() > 0:
        tipo_select.select_option(index=1)
        
    page.fill("input[name='fecha_compra']", "2026-01-15")
    page.fill("input[name='costo']", "250.00")
    
    # Enviar el formulario
    page.click("button[type='submit'], input[type='submit']")
    
    # Verificar redirección exitosa al dashboard
    expect(page).to_have_url(re.compile(r".*/inventario/?$"))

def test_ver_detalle_activo(page: Page):
    """
    Prueba E2E: Verifica la navegación y visualización 
    del detalle de un recurso específico.
    """
    page.goto("http://127.0.0.1:5001/inventario/")
    iniciar_sesion_si_es_necesario(page)

    detalle_link = page.locator("a[href*='/inventario/ver/']").first
    
    if detalle_link.count() > 0:
        detalle_link.click()
        expect(page).to_have_url(re.compile(r".*/inventario/ver/\d+$"))
    else:
        page.goto("http://127.0.0.1:5001/inventario/ver/1")
        expect(page).to_have_url(re.compile(r".*/inventario/ver/1$"))


def test_vista_gestion_asignaciones(page: Page):
    """
    Prueba E2E: Comprueba que la pantalla de gestión de asignaciones 
    cargue correctamente y muestre su título o tabla principal.
    """
    page.goto("http://127.0.0.1:5001/inventario/gestion-asignaciones")
    iniciar_sesion_si_es_necesario(page)

    expect(page).to_have_url(re.compile(r".*/inventario/gestion-asignaciones$"))
    
    header = page.locator("h1, h2, .card-title").filter(has_text=re.compile(r"asignacion|asignaciones", re.IGNORECASE))
    if header.count() > 0:
        expect(header.first).to_be_visible()


def test_editar_recurso(page: Page):
    """
    Prueba E2E: Verifica el flujo de edición de un recurso existente
    modificando sus datos y guardando los cambios.
    """
    page.goto("http://127.0.0.1:5001/inventario/")
    iniciar_sesion_si_es_necesario(page)

    # Buscamos el primer enlace o botón de editar de la lista de activos
    editar_link = page.locator("a[href*='/inventario/editar/']").first
    
    if editar_link.count() > 0:
        editar_link.click()
        expect(page).to_have_url(re.compile(r".*/inventario/editar/\d+$"))
    else:
        # Si no hay un enlace dinámico disponible en la tabla, accedemos a un ID de prueba fijo
        page.goto("http://127.0.0.1:5001/inventario/editar/1")
        expect(page).to_have_url(re.compile(r".*/inventario/editar/1$"))

    # Modificamos algunos campos del formulario de edición
    nombre_input = page.locator("input[name='nombre']")
    nombre_input.fill("Monitor Dell 24 Actualizado")
    
    costo_input = page.locator("input[name='costo']")
    if costo_input.count() > 0:
        costo_input.fill("275.50")

    # Guardamos los cambios enviando el formulario
    page.click("button[type='submit'], input[type='submit']")
    
    # Comprobamos que tras guardar redirige al listado o a la vista de detalle del recurso editado
    expect(page).to_have_url(re.compile(r".*/inventario(/(ver/\d+)?)?$"))