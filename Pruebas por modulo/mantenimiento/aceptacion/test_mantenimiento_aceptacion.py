from soporte_modulos import ruta


def test_mantenimiento_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('mantenimiento'))
    assert respuesta.status_code == 200
    assert respuesta.data
