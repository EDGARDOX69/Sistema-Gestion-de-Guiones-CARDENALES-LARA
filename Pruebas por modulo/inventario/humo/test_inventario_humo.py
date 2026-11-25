from soporte_modulos import ruta


def test_inventario_carga_para_superadmin(client, superadmin):
    respuesta = client.get(ruta('inventario'))
    assert respuesta.status_code == 200
    assert b'Error interno' not in respuesta.data
