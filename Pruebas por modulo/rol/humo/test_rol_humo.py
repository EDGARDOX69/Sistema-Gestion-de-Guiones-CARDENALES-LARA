from soporte_modulos import ruta


def test_rol_carga_para_superadmin(client, superadmin):
    respuesta = client.get(ruta('rol'))
    assert respuesta.status_code == 200
    assert b'Error interno' not in respuesta.data
