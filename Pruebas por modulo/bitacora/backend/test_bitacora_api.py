from soporte_modulos import es_publica, ruta


def test_bitacora_superadmin(client, superadmin):
    respuesta = client.get(ruta('bitacora'))
    assert respuesta.status_code == 200


def test_bitacora_sin_sesion(client):
    respuesta = client.get(ruta('bitacora'))
    if es_publica('bitacora'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
