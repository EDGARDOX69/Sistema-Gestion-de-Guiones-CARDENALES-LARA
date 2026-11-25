from soporte_modulos import ruta


def test_auth_login_publico(client):
    respuesta = client.get(ruta('auth'))
    assert respuesta.status_code == 200


def test_auth_sesion_activa_redirige_al_dashboard(client, superadmin):
    respuesta = client.get(ruta('auth'))
    assert respuesta.status_code == 302
    assert '/dashboard' in respuesta.headers['Location']
