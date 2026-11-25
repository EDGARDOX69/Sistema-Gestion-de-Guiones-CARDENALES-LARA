from soporte_modulos import RUTA_INTERFAZ


def test_auth_interfaz_carga(page):
    respuesta = page.goto(RUTA_INTERFAZ['auth'])
    assert respuesta.status == 200
    assert page.locator('body').inner_text().strip()
    assert 'Error interno' not in page.content()
