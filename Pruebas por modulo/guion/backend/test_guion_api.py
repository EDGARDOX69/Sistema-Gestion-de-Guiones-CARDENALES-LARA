from soporte_modulos import es_publica, ruta


def test_guion_superadmin(client, superadmin):
    respuesta = client.get(ruta('guion'))
    assert respuesta.status_code == 200


def test_guion_sin_sesion(client):
    respuesta = client.get(ruta('guion'))
    if es_publica('guion'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
