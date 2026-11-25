"""CP-BAL-ACE-01: flujo de aceptacion del modulo Balance.

El usuario administrativo consulta un contrato, registra un pago y descarga
el estado de cuenta. Todo ocurre contra ``estadio_db_test``.
"""

import uuid

from app.model.balance_model import Pago


def _crear_contrato(db, monto=10000.00):
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
                f'Empresa Aceptacion {sufijo}',
                f'J-{sufijo}',
                1,
                'Contacto Aceptacion',
                '04120000000',
                f'aceptacion_{sufijo}@prueba.com',
                1,
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
        return id_patrocinador, cur.lastrowid


def test_flujo_completo_de_balance(superadmin, client, db):
    id_patrocinador, id_contrato = _crear_contrato(db)
    referencia = f'UAT-{uuid.uuid4().hex[:10]}'

    respuesta = client.get('/balance/')
    assert respuesta.status_code == 200

    respuesta = client.get(f'/balance/api/contrato/{id_contrato}')
    assert respuesta.status_code == 200
    assert respuesta.get_json()['id_contrato'] == id_contrato

    respuesta = client.post('/balance/registrar-pago', data={
        'id_contrato': id_contrato,
        'monto': '250.00',
        'tipo_pago': 'Transferencia',
        'referencia': referencia,
        'fecha_pago': '2026-11-18',
        'hora_pago': '16:00',
        'descripcion': 'Validacion de aceptacion del modulo balance',
    })
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute(
            "SELECT monto, estado, registrado_por FROM pagos "
            "WHERE id_contrato = %s AND referencia = %s",
            (id_contrato, referencia),
        )
        pago = cur.fetchone()

    assert pago is not None
    assert float(pago['monto']) == 250.00
    assert pago['estado'] == 0
    assert pago['registrado_por'] == superadmin.id
    assert Pago().get_total_pagado_by_contrato(id_contrato) == 250.00

    respuesta = client.get(f'/balance/contrato/{id_contrato}/pdf')
    assert respuesta.status_code == 200
    assert respuesta.content_type == 'application/pdf'
