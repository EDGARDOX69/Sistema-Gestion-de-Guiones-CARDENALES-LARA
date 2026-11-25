from soporte_modulos import ruta


def test_en_vivo_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('en_vivo'))
    assert respuesta.status_code == 200
    assert respuesta.data
