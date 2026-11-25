from soporte_modulos import es_publica, ruta


def test_mantenimiento_superadmin(client, superadmin):
    respuesta = client.get(ruta('mantenimiento'))
    assert respuesta.status_code == 200


def test_mantenimiento_sin_sesion(client):
    respuesta = client.get(ruta('mantenimiento'))
    if es_publica('mantenimiento'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
