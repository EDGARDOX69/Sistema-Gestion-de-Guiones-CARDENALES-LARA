from soporte_modulos import es_publica, ruta


def test_reportes_superadmin(client, superadmin):
    respuesta = client.get(ruta('reportes'))
    assert respuesta.status_code == 200


def test_reportes_sin_sesion(client):
    respuesta = client.get(ruta('reportes'))
    if es_publica('reportes'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
