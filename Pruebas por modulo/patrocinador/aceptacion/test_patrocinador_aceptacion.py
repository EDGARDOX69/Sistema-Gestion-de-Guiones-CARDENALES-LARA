from soporte_modulos import ruta


def test_patrocinador_flujo_principal(client, superadmin):
    respuesta = client.get(ruta('patrocinador'))
    assert respuesta.status_code == 200
    assert respuesta.data
