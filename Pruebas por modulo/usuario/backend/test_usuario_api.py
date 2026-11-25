from soporte_modulos import es_publica, ruta


def test_usuario_superadmin(client, superadmin):
    respuesta = client.get(ruta('usuario'))
    assert respuesta.status_code == 200


def test_usuario_sin_sesion(client):
    respuesta = client.get(ruta('usuario'))
    if es_publica('usuario'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
