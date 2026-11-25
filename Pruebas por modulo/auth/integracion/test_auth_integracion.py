"""CP-AUT-INT-01: login, logout y proteccion de rutas."""

from flask import g

from soporte_api import cliente_anonimo, login_como


def test_login_valido_abre_el_dashboard(app, crear_usuario):
    usuario = crear_usuario(rol='Usuario')
    cliente = login_como(app, usuario)

    respuesta = cliente.get('/dashboard')
    assert respuesta.status_code == 200


def test_logout_cierra_la_sesion(app, crear_usuario):
    usuario = crear_usuario(rol='Usuario')
    cliente = login_como(app, usuario)

    respuesta = cliente.get('/auth/logout')
    assert respuesta.status_code == 302

    g.pop('_login_user', None)
    respuesta = cliente.get('/dashboard')
    assert respuesta.status_code == 401


def test_next_externo_no_redirige_fuera_del_sitio(app, crear_usuario):
    usuario = crear_usuario(rol='Usuario')
    g.pop('_login_user', None)
    cliente = app.test_client()
    with cliente.session_transaction() as sesion:
        sesion['captcha_code'] = 'ABCD'

    respuesta = cliente.post(
        '/auth/login?next=https://example.com',
        data={
            'email': usuario.email,
            'password': 'Clave1234',
            'captcha_text': 'ABCD',
        },
    )
    assert respuesta.status_code == 302
    assert 'example.com' not in respuesta.headers['Location']


def test_ruta_protegida_sin_sesion_devuelve_401(app):
    respuesta = cliente_anonimo(app).get('/dashboard')
    assert respuesta.status_code == 401
