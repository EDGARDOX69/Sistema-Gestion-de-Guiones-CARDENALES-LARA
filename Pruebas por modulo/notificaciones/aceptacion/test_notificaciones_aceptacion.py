from soporte_modulos import ruta


def test_notificaciones_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('notificaciones'))
    assert respuesta.status_code == 200
    assert respuesta.data
