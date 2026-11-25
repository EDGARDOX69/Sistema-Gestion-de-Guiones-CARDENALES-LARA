"""Utilidades para pruebas de API con varios actores."""

from flask import g


def login_como(app, usuario, password='Clave1234'):
    """Abre un cliente nuevo y limpia la cache de flask_login del contexto.

    El fixture ``_contexto`` mantiene un app context vivo; sin este ``pop``
    flask_login reutiliza el usuario anterior entre clientes.
    """
    g.pop('_login_user', None)
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion['captcha_code'] = 'ABCD'
    respuesta = client.post('/auth/login', data={
        'email': usuario.email,
        'password': password,
        'captcha_text': 'ABCD',
    })
    assert respuesta.status_code == 302
    return client


def cliente_anonimo(app):
    g.pop('_login_user', None)
    return app.test_client()
