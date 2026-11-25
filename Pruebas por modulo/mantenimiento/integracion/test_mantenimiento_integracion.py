"""CP-MAN-INT-01: ingreso, seguimiento, reparacion y baja de recursos."""

import uuid
from datetime import date


def _crear_recurso(db):
    nombre = f'Recurso Mantenimiento {uuid.uuid4().hex[:8]}'
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO recursos
                (nombre, descripcion, tipo_id, estado_id, fecha_compra,
                 costo, eliminado, creado_en)
            VALUES (%s, %s, 1, 1, CURDATE(), 50.00, 0, NOW())
            """,
            (nombre, 'Recurso para pruebas de mantenimiento'),
        )
        return cur.lastrowid, nombre


def _ingresar(client, recurso_id):
    return client.post(f'/mantenimiento/ingresar/{recurso_id}', data={
        'fecha_ingreso': date.today().isoformat(),
        'diagnostico': 'Diagnostico de prueba valido',
        'observaciones': 'Observaciones de prueba',
    })


def test_flujo_de_reparacion(superadmin, client, db):
    recurso_id, _ = _crear_recurso(db)

    respuesta = _ingresar(client, recurso_id)
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute(
            'SELECT * FROM mantenimientos WHERE recurso_id = %s ORDER BY id DESC LIMIT 1',
            (recurso_id,),
        )
        mantenimiento = cur.fetchone()
        cur.execute('SELECT estado_id FROM recursos WHERE id = %s', (recurso_id,))
        assert cur.fetchone()['estado_id'] == 3
    assert mantenimiento is not None
    assert mantenimiento['estado'] == 'en_espera'

    respuesta = client.post(f'/mantenimiento/agregar-nota/{mantenimiento["id"]}', data={
        'descripcion': 'Nota de seguimiento de la reparacion',
    })
    assert respuesta.status_code == 302

    respuesta = client.post(f'/mantenimiento/reparar/{mantenimiento["id"]}')
    assert respuesta.status_code == 302
    assert client.get(f'/mantenimiento/ver/{mantenimiento["id"]}').status_code == 200

    respuesta = client.post(f'/mantenimiento/reparar/{mantenimiento["id"]}')
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute('SELECT estado FROM mantenimientos WHERE id = %s', (mantenimiento['id'],))
        assert cur.fetchone()['estado'] == 'reparado'
        cur.execute('SELECT estado_id FROM recursos WHERE id = %s', (recurso_id,))
        assert cur.fetchone()['estado_id'] == 1
        cur.execute(
            'SELECT COUNT(*) AS total FROM historial_mantenimiento WHERE mantenimiento_id = %s',
            (mantenimiento['id'],),
        )
        assert cur.fetchone()['total'] >= 3


def test_dar_de_baja_un_recurso(superadmin, client, db):
    recurso_id, _ = _crear_recurso(db)
    _ingresar(client, recurso_id)

    with db.cursor() as cur:
        cur.execute(
            'SELECT id FROM mantenimientos WHERE recurso_id = %s ORDER BY id DESC LIMIT 1',
            (recurso_id,),
        )
        mantenimiento_id = cur.fetchone()['id']

    respuesta = client.post(f'/mantenimiento/dar-baja/{mantenimiento_id}')
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute('SELECT estado FROM mantenimientos WHERE id = %s', (mantenimiento_id,))
        assert cur.fetchone()['estado'] == 'baja'
        cur.execute('SELECT estado_id FROM recursos WHERE id = %s', (recurso_id,))
        assert cur.fetchone()['estado_id'] == 5
