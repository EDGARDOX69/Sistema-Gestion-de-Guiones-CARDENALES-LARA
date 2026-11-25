from soporte_modulos import ruta


def test_guion_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('guion'))
    assert respuesta.status_code == 200
    assert respuesta.data
