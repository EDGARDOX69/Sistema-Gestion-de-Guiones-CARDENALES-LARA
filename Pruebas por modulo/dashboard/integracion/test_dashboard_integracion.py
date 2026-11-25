"""CP-DAS-INT-01: panel principal y control de acceso."""

from soporte_api import cliente_anonimo, login_como


def test_dashboard_anonimo_devuelve_401_json(app):
    respuesta = cliente_anonimo(app).get('/dashboard')
    assert respuesta.status_code == 401
    assert respuesta.is_json


def test_dashboard_responde_para_superadmin(superadmin, client):
    respuesta = client.get('/dashboard')
    assert respuesta.status_code == 200
    assert b'/dashboard' in respuesta.data or b'Dashboard' in respuesta.data


def test_dashboard_responde_para_rol_basico(app, crear_usuario):
    usuario = crear_usuario(rol='Usuario')
    cliente = login_como(app, usuario)

    respuesta = cliente.get('/dashboard')
    assert respuesta.status_code == 200
