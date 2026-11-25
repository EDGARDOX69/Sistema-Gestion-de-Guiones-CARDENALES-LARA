from soporte_modulos import ruta


def test_guion_carga_para_superadmin(client, superadmin):
    respuesta = client.get(ruta('guion'))
    assert respuesta.status_code == 200
    assert b'Error interno' not in respuesta.data
