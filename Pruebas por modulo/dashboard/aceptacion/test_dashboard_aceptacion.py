from soporte_modulos import ruta


def test_dashboard_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('dashboard'))
    assert respuesta.status_code == 200
    assert respuesta.data
