from soporte_modulos import ruta


def test_rol_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('rol'))
    assert respuesta.status_code == 200
    assert respuesta.data
