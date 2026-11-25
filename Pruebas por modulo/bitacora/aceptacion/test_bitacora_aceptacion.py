from soporte_modulos import ruta


def test_bitacora_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('bitacora'))
    assert respuesta.status_code == 200
    assert respuesta.data
