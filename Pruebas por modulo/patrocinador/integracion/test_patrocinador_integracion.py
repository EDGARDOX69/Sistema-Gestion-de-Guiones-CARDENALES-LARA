"""CP-PAT-INT-01: CRUD de patrocinadores y aislamiento de la baja logica."""

import uuid


def _datos(sufijo, encargado_id):
    return {
        'nombre_empresa': f'Patrocinador {sufijo}',
        'rif': f'J-{str(uuid.uuid4().int)[:8]}',
        'tipo_contrato': '1',
        'nombre_contacto': 'Contacto Prueba',
        'telefono': '04120000000',
        'email': f'patrocinador_{sufijo}@prueba.com',
        'encargado_id': encargado_id,
    }


def test_crud_de_patrocinador(superadmin, client, db):
    sufijo = uuid.uuid4().hex[:8]
    datos = _datos(sufijo, superadmin.id)

    respuesta = client.post('/patrocinador/', data={'registrar': '1', **datos})
    assert respuesta.status_code == 200
    assert 'registrado' in respuesta.get_json()['mensaje'].lower()

    with db.cursor() as cur:
        cur.execute(
            'SELECT * FROM patrocinadores WHERE nombre_empresa = %s',
            (datos['nombre_empresa'],),
        )
        patrocinador = cur.fetchone()
    assert patrocinador is not None
    assert patrocinador['estado'] == 1
    assert patrocinador['encargado_id'] == superadmin.id

    respuesta = client.get(f'/patrocinador/api/obtener/{patrocinador["id_patrocinador"]}')
    assert respuesta.status_code == 200
    assert respuesta.get_json()['nombre_empresa'] == datos['nombre_empresa']

    datos_editados = dict(datos)
    datos_editados['telefono'] = '04120000001'
    respuesta = client.post('/patrocinador/', data={
        'editar': patrocinador['id_patrocinador'],
        **datos_editados,
    })
    assert respuesta.status_code == 200
    assert 'actualizado' in respuesta.get_json()['mensaje'].lower()

    respuesta = client.post('/patrocinador/', data={
        'eliminar': patrocinador['id_patrocinador'],
    })
    assert respuesta.status_code == 200

    with db.cursor() as cur:
        cur.execute(
            'SELECT estado FROM patrocinadores WHERE id_patrocinador = %s',
            (patrocinador['id_patrocinador'],),
        )
        assert cur.fetchone()['estado'] == 0


def test_tipo_de_contrato_invalido_se_rechaza(superadmin, client):
    respuesta = client.post('/patrocinador/', data={
        'registrar': '1',
        'nombre_empresa': 'Patrocinador Invalido',
        'rif': 'J-12345678',
        'tipo_contrato': '9',
        'encargado_id': superadmin.id,
    })
    assert respuesta.status_code == 400
    assert 'inválido' in respuesta.get_json()['error'].lower()
