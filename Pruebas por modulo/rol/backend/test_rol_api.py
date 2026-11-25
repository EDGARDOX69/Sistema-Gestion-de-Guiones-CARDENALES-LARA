from soporte_modulos import es_publica, ruta


def test_rol_superadmin(client, superadmin):
    respuesta = client.get(ruta('rol'))
    assert respuesta.status_code == 200


def test_rol_sin_sesion(client):
    respuesta = client.get(ruta('rol'))
    if es_publica('rol'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
