"""CP-BAL-UI-01: humo visual del modulo Balance en escritorio y movil."""

from soporte_ui import login


def test_balance_carga_para_un_operador(page, e2e_credenciales):
    login(page, e2e_credenciales)

    respuesta = page.goto('/balance/')
    assert respuesta.status == 200
    assert page.title()
    assert page.locator('body').inner_text().strip()
    assert 'Error interno' not in page.content()


def test_balance_movil_sin_desbordamiento_horizontal(page, e2e_credenciales):
    login(page, e2e_credenciales)
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto('/balance/')

    desborda = page.evaluate(
        '() => document.documentElement.scrollWidth > window.innerWidth'
    )
    assert not desborda
