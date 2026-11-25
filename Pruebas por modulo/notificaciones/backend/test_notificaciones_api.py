from soporte_modulos import es_publica, ruta


def test_notificaciones_superadmin(client, superadmin):
    respuesta = client.get(ruta('notificaciones'))
    assert respuesta.status_code == 200


def test_notificaciones_sin_sesion(client):
    respuesta = client.get(ruta('notificaciones'))
    if es_publica('notificaciones'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
