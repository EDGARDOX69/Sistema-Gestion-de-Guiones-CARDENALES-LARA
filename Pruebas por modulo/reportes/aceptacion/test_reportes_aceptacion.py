from soporte_modulos import ruta


def test_reportes_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('reportes'))
    assert respuesta.status_code == 200
    assert respuesta.data
