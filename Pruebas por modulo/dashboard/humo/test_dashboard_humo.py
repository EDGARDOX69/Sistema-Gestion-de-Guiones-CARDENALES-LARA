from soporte_modulos import ruta


def test_dashboard_carga_para_superadmin(client, superadmin):
    respuesta = client.get(ruta('dashboard'))
    assert respuesta.status_code == 200
    assert b'Error interno' not in respuesta.data
