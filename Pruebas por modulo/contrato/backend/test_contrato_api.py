from soporte_modulos import es_publica, ruta


def test_contrato_superadmin(client, superadmin):
    respuesta = client.get(ruta('contrato'))
    assert respuesta.status_code == 200


def test_contrato_sin_sesion(client):
    respuesta = client.get(ruta('contrato'))
    if es_publica('contrato'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
