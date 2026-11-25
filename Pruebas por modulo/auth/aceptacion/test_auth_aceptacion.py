from soporte_modulos import ruta


def test_auth_flujo_principal(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin')
    respuesta = login(usuario)
    assert respuesta.status_code == 302
    assert '/dashboard' in respuesta.headers['Location']

    panel = client.get('/dashboard')
    assert panel.status_code == 200

    salida = client.get('/auth/logout')
    assert salida.status_code == 302

    assert client.get(ruta('auth')).status_code == 200
