from soporte_modulos import es_publica, ruta


def test_premio_superadmin(client, superadmin):
    respuesta = client.get(ruta('premio'))
    assert respuesta.status_code == 200


def test_premio_sin_sesion(client):
    respuesta = client.get(ruta('premio'))
    if es_publica('premio'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
