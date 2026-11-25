from soporte_modulos import ruta


def test_gestion_tarea_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('gestion_tarea'))
    assert respuesta.status_code == 200
    assert respuesta.data
