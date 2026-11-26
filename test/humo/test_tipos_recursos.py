import pytest
from playwright.sync_api import Page, expect

def test_smoke_modal_tipos_recurso_apertura(page: Page):
    """
    Prueba de Humo 1 (UI): Abre la interfaz de inventario y verifica 
    que el modal dedicado a la gestión de Tipos de Recurso esté disponible.
    """
    page.goto("http://127.0.0.1:5001/inventario/")
    
    # Localizar el disparador exclusivo del modal de tipos de activo
    btn_modal = page.locator("[data-bs-target='#formulario_tipo_activo']")
    expect(btn_modal).to_be_visible()
    btn_modal.click()
    
    # Comprobar que el modal de tipos de activo se despliega correctamente
    modal = page.locator("#formulario_tipo_activo")
    expect(modal).to_be_visible()


def test_smoke_elementos_formulario_tipo_recurso(page: Page):
    """
    Prueba de Humo 2 (UI): Valida que los campos específicos del formulario 
    de registro de Tipos de Recurso (nombre y descripción) existan en el DOM.
    """
    page.goto("http://127.0.0.1:5001/inventario/")
    
    # Abrir el modal de tipos de activo
    page.locator("[data-bs-target='#formulario_tipo_activo']").click()
    
    # Validar campos específicos del formulario de tipos de recurso
    expect(page.locator("#nombre_tipo_activo")).to_be_attached()
    expect(page.locator("#descripcion_tipo_activo")).to_be_attached()
    expect(page.locator("#btnTipoActivo")).to_be_attached()


def test_smoke_tabla_tipos_recurso_render(page: Page):
    """
    Prueba de Humo 3 (UI): Verifica que la tabla contenedora de los 
    tipos de recurso ('tipoActivoTable') cargue en la interfaz.
    """
    page.goto("http://127.0.0.1:5001/inventario/")
    
    # Abrir el modal donde se encuentra la tabla de tipos de activo
    page.locator("[data-bs-target='#formulario_tipo_activo']").click()
    
    # Comprobar la presencia de la tabla exclusiva de tipos de activo
    tabla_tipos = page.locator("#tipoActivoTable")
    expect(tabla_tipos).to_be_visible()

    import pytest
from playwright.sync_api import Page, expect
import pytest
from playwright.sync_api import Page, expect
