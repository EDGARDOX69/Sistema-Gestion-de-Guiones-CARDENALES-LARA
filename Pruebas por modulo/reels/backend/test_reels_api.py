from soporte_modulos import es_publica, ruta


def test_reels_superadmin(client, superadmin):
    respuesta = client.get(ruta('reels'))
    assert respuesta.status_code == 200


def test_reels_sin_sesion(client):
    respuesta = client.get(ruta('reels'))
    if es_publica('reels'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
