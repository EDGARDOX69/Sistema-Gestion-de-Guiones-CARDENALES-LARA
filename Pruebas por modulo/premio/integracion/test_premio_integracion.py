"""CP-PRE-INT-01: registro, entrega parcial y baja logica de premios."""

import uuid


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
                f'Patrocinador Premio {sufijo}',
                f'J-{str(uuid.uuid4().int)[:8]}',
                1,
                'Contacto Premio',
                '04120000000',
                f'premio_{sufijo}@prueba.com',
                encargado_id,
            ),
        )
        return cur.lastrowid


def test_registrar_entregar_y_eliminar_premio(superadmin, client, db):
    id_patrocinador = _crear_patrocinador(db, superadmin.id)
    nombre = f'Premio {uuid.uuid4().hex[:8]}'

    respuesta = client.post('/premio/', data={
        'accion': 'registrar',
        'nombre': nombre,
        'id_patrocinador': id_patrocinador,
        'descripcion': 'Premio de prueba',
        'cantidad': '3',
    })
    assert respuesta.status_code == 200
    assert 'registrado' in respuesta.get_json()['mensaje'].lower()

    with db.cursor() as cur:
        cur.execute('SELECT * FROM premios WHERE nombre = %s', (nombre,))
        premio = cur.fetchone()
    assert premio is not None
    assert premio['estado'] == 'pendiente'
    assert premio['cantidad'] == 3
    assert premio['foto'] == 'default-premio.png'

    respuesta = client.post('/premio/', data={
        'accion': 'entregar',
        'id_premio': premio['id'],
        'id_patrocinador': id_patrocinador,
        'cantidad_entregar': '1',
        'descripcion': 'Primera entrega',
    })
    assert respuesta.status_code == 200

    with db.cursor() as cur:
        cur.execute(
            'SELECT estado, cantidad_entregada FROM premios WHERE id = %s',
            (premio['id'],),
        )
        parcial = cur.fetchone()
    assert parcial['estado'] == 'pendiente'
    assert parcial['cantidad_entregada'] == 1

    respuesta = client.post('/premio/', data={
        'accion': 'entregar',
        'id_premio': premio['id'],
        'id_patrocinador': id_patrocinador,
        'cantidad_entregar': '2',
        'descripcion': 'Entrega final',
    })
    assert respuesta.status_code == 200

    with db.cursor() as cur:
        cur.execute(
            'SELECT estado, cantidad_entregada, entregado_por '
            'FROM premios WHERE id = %s',
            (premio['id'],),
        )
        final = cur.fetchone()
    assert final['estado'] == 'entregado'
    assert final['cantidad_entregada'] == 3
    assert final['entregado_por'] == superadmin.id

    respuesta = client.post('/premio/', data={
        'accion': 'obtener',
        'id': premio['id'],
    })
    assert respuesta.status_code == 200
    assert respuesta.get_json()['cantidad_entregada'] == 3

    respuesta = client.post('/premio/', data={
        'accion': 'eliminar',
        'id': premio['id'],
    })
    assert respuesta.status_code == 200

    with db.cursor() as cur:
        cur.execute('SELECT estatus FROM premios WHERE id = %s', (premio['id'],))
        assert cur.fetchone()['estatus'] == 1


def test_entregar_premio_inexistente_devuelve_400(superadmin, client, db):
    id_patrocinador = _crear_patrocinador(db, superadmin.id)

    respuesta = client.post('/premio/', data={
        'accion': 'entregar',
        'id_premio': 999999,
        'id_patrocinador': id_patrocinador,
        'cantidad_entregar': '1',
    })
    assert respuesta.status_code == 400
