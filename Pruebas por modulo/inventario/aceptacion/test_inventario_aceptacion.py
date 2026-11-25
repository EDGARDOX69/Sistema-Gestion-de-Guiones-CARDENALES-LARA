from soporte_modulos import ruta


def test_inventario_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('inventario'))
    assert respuesta.status_code == 200
    assert respuesta.data
