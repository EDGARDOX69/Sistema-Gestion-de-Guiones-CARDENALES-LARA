"""CP-CON-INT-01: CRUD de contratos y consulta por API."""

import uuid

from app.model.contrato_model import ContratoModel


def _crear_patrocinador(db, encargado_id):
    sufijo = uuid.uuid4().hex[:8]
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO patrocinadores
                (nombre_empresa, rif, tipo_contrato, nombre_contacto,
                 telefono, email, estado, encargado_id)
            VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
            """,
            (
                f'Patrocinador Contrato {sufijo}',
                f'J-{str(uuid.uuid4().int)[:8]}',
                1,
                'Contacto Contrato',
                '04120000000',
                f'contrato_{sufijo}@prueba.com',
                encargado_id,
            ),
        )
        return cur.lastrowid


def test_crud_de_contrato(superadmin, client, db):
    id_patrocinador = _crear_patrocinador(db, superadmin.id)

    respuesta = client.post('/contratos/', data={
        'registrar': '1',
        'id_patrocinador': id_patrocinador,
        'fecha_inicio': '2026-01-01',
        'fecha_fin': '2026-12-31',
        'tipo': '1',
        'monto_total': '5000.00',
        'estatus': 'Vigente',
    })
    assert respuesta.status_code == 200
    assert 'registrado' in respuesta.get_json()['mensaje'].lower()

    with db.cursor() as cur:
        cur.execute(
            'SELECT * FROM contrato WHERE id_patrocinador = %s '
            'ORDER BY id_contrato DESC LIMIT 1',
            (id_patrocinador,),
        )
        contrato = cur.fetchone()
    assert contrato is not None
    assert str(contrato['estado']) == '1'
    assert float(contrato['monto_total']) == 5000.00

    respuesta = client.get(f'/contratos/api/obtener/{contrato["id_contrato"]}')
    assert respuesta.status_code == 200
    assert respuesta.get_json()['estatus'] == 'Vigente'

    respuesta = client.post('/contratos/', data={
        'editar': contrato['id_contrato'],
        'id_patrocinador': id_patrocinador,
        'fecha_inicio': '2026-01-01',
        'fecha_fin': '2026-12-31',
        'tipo': '2',
        'monto_total': '6500.00',
        'estatus': 'Vigente',
    })
    assert respuesta.status_code == 200
    assert 'actualizado' in respuesta.get_json()['mensaje'].lower()

    actualizado = ContratoModel().obtener_por_id(contrato['id_contrato'])
    assert actualizado['tipo'] == '2'
    assert float(actualizado['monto_total']) == 6500.00

    respuesta = client.post('/contratos/', data={
        'eliminar': contrato['id_contrato'],
    })
    assert respuesta.status_code == 200

    with db.cursor() as cur:
        cur.execute(
            'SELECT estado FROM contrato WHERE id_contrato = %s',
            (contrato['id_contrato'],),
        )
        assert str(cur.fetchone()['estado']) == '0'


def test_tipo_invalido_y_contrato_inexistente(superadmin, client, db):
    id_patrocinador = _crear_patrocinador(db, superadmin.id)

    respuesta = client.post('/contratos/', data={
        'registrar': '1',
        'id_patrocinador': id_patrocinador,
        'fecha_inicio': '2026-01-01',
        'fecha_fin': '2026-12-31',
        'tipo': '9',
    })
    assert respuesta.status_code == 400
    assert 'inválido' in respuesta.get_json()['error'].lower()

    respuesta = client.get('/contratos/api/obtener/999999')
    assert respuesta.status_code == 404
