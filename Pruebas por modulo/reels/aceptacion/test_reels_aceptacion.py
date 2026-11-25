from soporte_modulos import ruta


def test_reels_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('reels'))
    assert respuesta.status_code == 200
    assert respuesta.data
