"""CP-ENV-INT-01: ciclo basico de un guion en vivo y errores controlados."""


def test_iniciar_ver_y_finalizar_guion_en_vivo(superadmin, client, crear_guion_completo):
    guion_id = crear_guion_completo(nombre='Guion En Vivo Prueba')

    respuesta = client.get(f'/en-vivo/iniciar/{guion_id}')
    assert respuesta.status_code == 302

    respuesta = client.get(f'/en-vivo/{guion_id}')
    assert respuesta.status_code == 200

    respuesta = client.get(f'/en-vivo/api/estado-actual/{guion_id}')
    assert respuesta.status_code == 200
    assert respuesta.get_json()['guion_id'] == guion_id
    assert isinstance(respuesta.get_json()['estados'], list)

    respuesta = client.get(f'/en-vivo/finalizar/{guion_id}')
    assert respuesta.status_code == 302

    respuesta = client.get(f'/en-vivo/{guion_id}')
    assert respuesta.status_code == 302


def test_sincronizar_sin_json_no_devuelve_500(
    superadmin, client, crear_guion_completo
):
    guion_id = crear_guion_completo(nombre='Guion Sin JSON')

    respuesta = client.post(f'/en-vivo/api/sincronizar/{guion_id}')
    assert respuesta.status_code < 500


def test_guiones_por_fecha_sin_json_no_devuelve_500(superadmin, client):
    respuesta = client.post('/en-vivo/api/guiones-por-fecha')
    assert respuesta.status_code < 500
