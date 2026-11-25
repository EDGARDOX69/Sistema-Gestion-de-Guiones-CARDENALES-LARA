"""CP-TAR-INT-01: asignacion, permisos y notificacion al completar tareas."""

import uuid

from flask import g


def _login_como(app, usuario, password='Clave1234'):
    g.pop('_login_user', None)
    client = app.test_client()
    with client.session_transaction() as sesion:
        sesion['captcha_code'] = 'ABCD'
    respuesta = client.post('/auth/login', data={
        'email': usuario.email,
        'password': password,
        'captcha_text': 'ABCD',
    })
    assert respuesta.status_code == 302
    return client


def test_solo_el_asignado_o_supervisor_completa_la_tarea(
    superadmin, client, crear_usuario, db, seguridad_db
):
    nombre = f'Tarea {uuid.uuid4().hex[:8]}'
    respuesta = client.post('/gestion-tarea/', data={
        'registrar': '1',
        'Nombre_Tarea': nombre,
        'Instruccion': 'Instruccion de prueba para la tarea',
    })
    assert respuesta.status_code == 200
    assert respuesta.get_json()['success'] is True

    with db.cursor() as cur:
        cur.execute('SELECT id_tarea FROM tareas WHERE Nombre_Tarea = %s', (nombre,))
        tarea_id = cur.fetchone()['id_tarea']

    asignado = crear_usuario(rol='Usuario')
    ajeno = crear_usuario(rol='Usuario')

    respuesta = client.post('/gestion-tarea/', data={
        'asignar': '1',
        'id_tarea': tarea_id,
        'id_usuarios': [asignado.id],
    })
    assert respuesta.status_code == 200
    assert respuesta.get_json()['asignados'] == 1

    with db.cursor() as cur:
        cur.execute(
            'SELECT id_asignacion, id_usuario, Estado FROM tareas_asignadas '
            'WHERE id_tarea = %s AND id_usuario = %s',
            (tarea_id, asignado.id),
        )
        asignacion = cur.fetchone()
    assert asignacion is not None

    cliente_ajeno = _login_como(client.application, ajeno)
    respuesta = cliente_ajeno.post(
        '/gestion-tarea/completar',
        data={'id_asignacion': asignacion['id_asignacion']},
        headers={'Accept': 'application/json'},
    )
    assert respuesta.status_code == 403

    with db.cursor() as cur:
        cur.execute(
            'SELECT Estado FROM tareas_asignadas WHERE id_asignacion = %s',
            (asignacion['id_asignacion'],),
        )
        assert cur.fetchone()['Estado'] != 'Completada'

    cliente_asignado = _login_como(client.application, asignado)
    respuesta = cliente_asignado.post(
        '/gestion-tarea/completar',
        data={'id_asignacion': asignacion['id_asignacion']},
        headers={'Accept': 'application/json'},
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()['success'] is True

    with db.cursor() as cur:
        cur.execute(
            'SELECT Estado FROM tareas_asignadas WHERE id_asignacion = %s',
            (asignacion['id_asignacion'],),
        )
        assert cur.fetchone()['Estado'] == 'Completada'

    with seguridad_db.cursor() as cur:
        cur.execute(
            'SELECT COUNT(*) AS total FROM notificaciones '
            'WHERE usuario_id = %s AND tipo = %s',
            (superadmin.id, 'tarea_completada'),
        )
        assert cur.fetchone()['total'] >= 1
