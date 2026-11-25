from soporte_modulos import RUTA_INTERFAZ
from soporte_ui import login


def test_usuario_interfaz_carga(page, e2e_credenciales):
    login(page, e2e_credenciales)
    respuesta = page.goto(RUTA_INTERFAZ['usuario'])
    assert respuesta.status == 200
    assert page.locator('body').inner_text().strip()
    assert 'Error interno' not in page.content()
