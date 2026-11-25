from soporte_modulos import ruta


def test_chat_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('chat'))
    assert respuesta.status_code == 200
    assert respuesta.data
