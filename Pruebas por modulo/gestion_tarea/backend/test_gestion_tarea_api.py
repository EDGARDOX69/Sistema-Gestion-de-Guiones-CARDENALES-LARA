from soporte_modulos import es_publica, ruta


def test_gestion_tarea_superadmin(client, superadmin):
    respuesta = client.get(ruta('gestion_tarea'))
    assert respuesta.status_code == 200


def test_gestion_tarea_sin_sesion(client):
    respuesta = client.get(ruta('gestion_tarea'))
    if es_publica('gestion_tarea'):
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code != 200
