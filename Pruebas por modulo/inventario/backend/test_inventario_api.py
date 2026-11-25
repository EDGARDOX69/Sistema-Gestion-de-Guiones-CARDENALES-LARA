from soporte_modulos import es_publica, ruta


def test_inventario_superadmin(client, superadmin):
    respuesta = client.get(ruta('inventario'))
    assert respuesta.status_code == 200


def test_inventario_sin_sesion(client):
    respuesta = client.get(ruta('inventario'))
    if es_publica('inventario'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
