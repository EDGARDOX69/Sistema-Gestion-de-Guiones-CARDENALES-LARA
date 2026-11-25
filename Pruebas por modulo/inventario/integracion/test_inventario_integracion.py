"""CP-INV-INT-01: asignacion y devolucion de recursos."""

import uuid

from app.model.inventario_model import InventarioModel


def _crear_recurso(db):
    nombre = f'Recurso {uuid.uuid4().hex[:8]}'
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO recursos
                (nombre, descripcion, tipo_id, estado_id, fecha_compra,
                 costo, eliminado, creado_en)
            VALUES (%s, %s, 1, 1, CURDATE(), 100.00, 0, NOW())
            """,
            (nombre, 'Recurso de prueba de inventario'),
        )
        return cur.lastrowid, nombre


def test_asignar_y_devolver_recurso(superadmin, client, db):
    recurso_id, nombre = _crear_recurso(db)

    respuesta = client.post(f'/inventario/asignar/{recurso_id}', data={
        'usuario_id': superadmin.id,
        'fecha_devolucion_esperada': '2026-12-31',
        'notas': 'Asignacion de prueba',
    })
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute(
            'SELECT * FROM asignaciones_recursos WHERE recurso_id = %s',
            (recurso_id,),
        )
        asignacion = cur.fetchone()
        cur.execute('SELECT estado_id FROM recursos WHERE id = %s', (recurso_id,))
        estado = cur.fetchone()['estado_id']

    assert asignacion is not None
    assert asignacion['fecha_devolucion_real'] is None
    assert asignacion['usuario_id'] == superadmin.id
    assert estado == 2

    respuesta = client.post(f'/inventario/asignar/{recurso_id}', data={
        'usuario_id': superadmin.id,
    })
    assert respuesta.status_code == 200

    with db.cursor() as cur:
        cur.execute(
            'SELECT COUNT(*) AS total FROM asignaciones_recursos WHERE recurso_id = %s',
            (recurso_id,),
        )
        assert cur.fetchone()['total'] == 1

    respuesta = client.post(f'/inventario/devolver/{asignacion["id"]}')
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute(
            'SELECT fecha_devolucion_real, estado_asignacion_id '
            'FROM asignaciones_recursos WHERE id = %s',
            (asignacion['id'],),
        )
        devuelta = cur.fetchone()
        cur.execute('SELECT estado_id FROM recursos WHERE id = %s', (recurso_id,))
        estado = cur.fetchone()['estado_id']

    assert devuelta['fecha_devolucion_real'] is not None
    assert devuelta['estado_asignacion_id'] == 2
    assert estado == 1

    respuesta = client.post(f'/inventario/devolver/{asignacion["id"]}')
    assert respuesta.status_code == 302


def test_consultar_asignaciones_usa_el_esquema_de_prueba(superadmin, client, db):
    recurso_id, _ = _crear_recurso(db)
    client.post(f'/inventario/asignar/{recurso_id}', data={
        'usuario_id': superadmin.id,
    })

    asignaciones = InventarioModel().consultar_asignaciones(recurso_id=recurso_id)
    assert len(asignaciones) == 1
    assert asignaciones[0]['usuario_nombre'] == superadmin.nombre
