from soporte_modulos import es_publica, ruta


def test_chat_superadmin(client, superadmin):
    respuesta = client.get(ruta('chat'))
    assert respuesta.status_code == 200


def test_chat_sin_sesion(client):
    respuesta = client.get(ruta('chat'))
    if es_publica('chat'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
