from soporte_modulos import ruta


def test_contrato_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('contrato'))
    assert respuesta.status_code == 200
    assert respuesta.data
