from soporte_modulos import es_publica, ruta


def test_patrocinador_superadmin(client, superadmin):
    respuesta = client.get(ruta('patrocinador'))
    assert respuesta.status_code == 200


def test_patrocinador_sin_sesion(client):
    respuesta = client.get(ruta('patrocinador'))
    if es_publica('patrocinador'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
