from soporte_modulos import es_publica, ruta


def test_en_vivo_superadmin(client, superadmin):
    respuesta = client.get(ruta('en_vivo'))
    assert respuesta.status_code == 200


def test_en_vivo_sin_sesion(client):
    respuesta = client.get(ruta('en_vivo'))
    if es_publica('en_vivo'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
