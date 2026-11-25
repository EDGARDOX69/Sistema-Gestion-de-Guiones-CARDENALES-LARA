"""CP-BAL-API-01: endpoints del modulo Balance con sesion autorizada."""

import uuid

import pytest

pytestmark = pytest.mark.api


def _preparar_contrato(db, monto=5000.00):
    sufijo = uuid.uuid4().hex[:8]
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO patrocinadores
                (nombre_empresa, rif, tipo_contrato, nombre_contacto,
                 telefono, email, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f'Sponsor API {sufijo}', f'J-{sufijo}', 1,
                'Contacto API', '04120000000',
                f'api_{sufijo}@prueba.com', 1,
            ),
        )
        id_patrocinador = cur.lastrowid
        cur.execute(
            """
            INSERT INTO contrato
                (id_patrocinador, fecha_inicio, fecha_fin, estado,
                 estatus, tipo, monto_total)
            VALUES (%s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR),
                    %s, %s, %s, %s)
            """,
            (id_patrocinador, '1', 'Vigente', '1', monto),
        )
        return cur.lastrowid


def test_endpoints_de_balance(superadmin, client, db):
    id_contrato = _preparar_contrato(db)
    referencia = f'API-{uuid.uuid4().hex[:10]}'

    respuesta = client.get('/balance/')
    assert respuesta.status_code == 200

    respuesta = client.get(f'/balance/api/contrato/{id_contrato}')
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert cuerpo['id_contrato'] == id_contrato
    assert cuerpo['saldo_pendiente'] == 5000.00

    respuesta = client.post('/balance/registrar-pago', data={
        'id_contrato': id_contrato,
        'monto': '1000.00',
        'tipo_pago': 'Transferencia',
        'referencia': referencia,
        'fecha_pago': '2026-11-18',
        'hora_pago': '10:00',
        'descripcion': 'Abono de prueba API',
    })
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute(
            'SELECT id_pago FROM pagos WHERE id_contrato = %s AND referencia = %s',
            (id_contrato, referencia),
        )
        pago = cur.fetchone()
    assert pago is not None

    respuesta = client.get(f'/balance/api/pago/{pago["id_pago"]}')
    assert respuesta.status_code == 200
    assert respuesta.get_json()['monto'] == 1000.00

    respuesta = client.get(f'/balance/contrato/{id_contrato}/pdf')
    assert respuesta.status_code == 200
    assert respuesta.content_type == 'application/pdf'
