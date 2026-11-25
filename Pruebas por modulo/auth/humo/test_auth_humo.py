from soporte_modulos import ruta


def test_auth_login_carga_sin_sesion(client):
    respuesta = client.get(ruta('auth'))
    assert respuesta.status_code == 200
    assert b'Error interno' not in respuesta.data
