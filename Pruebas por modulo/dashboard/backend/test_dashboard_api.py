from soporte_modulos import es_publica, ruta


def test_dashboard_superadmin(client, superadmin):
    respuesta = client.get(ruta('dashboard'))
    assert respuesta.status_code == 200


def test_dashboard_sin_sesion(client):
    respuesta = client.get(ruta('dashboard'))
    if es_publica('dashboard'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
