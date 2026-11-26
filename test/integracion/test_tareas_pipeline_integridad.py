"""PL-TAR-INT — Garantías de integridad del pipeline de asignación de tareas.

Complementa la suite existente con tres casos de frontera que no estaban
cubiertos: reversión transaccional, usuarios inactivos y dedupe de las tres
fuentes de destino a la vez (multi-select + campo legacy + departamento).

Todo corre sobre ``estadio_db_test`` / ``seguridad_test``. Los nombres se
generan con ``uuid`` porque las bases se clonan una sola vez por sesión.
"""
import uuid

from app import config
from app.database import Database
from app.model.auth_model import UsuarioModel
from app.model.tarea_model import TareaModel, TareasAsignadasModel


def _crear_tarea(creador_id):
    modelo = TareaModel()
    modelo.set_nombre_tarea(f'Tarea pipeline {uuid.uuid4().hex[:8]}')
    modelo.set_instruccion('Instrucción suficientemente larga para el pipeline')
    modelo.set_id_usuario_creador(creador_id)
    return modelo.confirmar_registro()


def _filas(esquema, sql, params=()):
    with Database.get_connection(esquema).cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def _total(esquema, sql, params=()):
    return _filas(esquema, sql, params)[0]['total']


def test_pl_tar_int_01_fallo_notificacion_revierte_asignacion(app, superadmin, crear_usuario):
    """Si falla el INSERT en seguridad, no queda ninguna asignación huérfana."""
    id_tarea = _crear_tarea(superadmin.id)
    destinatario = crear_usuario()

    # Esquema inexistente: el INSERT de la notificación falla DENTRO de la
    # transacción que ya insertó la asignación. Se restaura en `finally` para
    # que las consultas de verificación sigan apuntando a seguridad_test.
    cfg = config.DATABASE_CONFIG['seguridad']
    esquema_original = cfg['database']
    cfg['database'] = 'seguridad_inexistente_pipeline'
    try:
        asignados, omitidos = TareasAsignadasModel().asignar_a_usuarios(
            id_tarea, [destinatario.id], 'Tarea rollback', superadmin.nombre
        )
    finally:
        cfg['database'] = esquema_original

    assert asignados is None and omitidos is None
    assert _total(
        'estadio_db_test',
        'SELECT COUNT(*) total FROM tareas_asignadas WHERE id_tarea = %s',
        (id_tarea,),
    ) == 0
    assert _total(
        'seguridad',
        'SELECT COUNT(*) total FROM notificaciones WHERE usuario_id = %s',
        (destinatario.id,),
    ) == 0


def test_pl_tar_int_02_inactivo_no_recibe_asignacion_ni_notificacion(
    app, client, superadmin, crear_usuario
):
    """`filtrar_ids_activos` descarta al inactivo antes de escribir nada."""
    activo = crear_usuario()
    inactivo = crear_usuario(activo=False)
    id_tarea = _crear_tarea(superadmin.id)

    respuesta = client.post('/gestion-tarea/', data={
        'asignar': 'true',
        'id_tarea': str(id_tarea),
        'id_usuarios': [str(activo.id), str(inactivo.id), str(inactivo.id)],
    })
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {'success': True, 'asignados': 1, 'omitidos': 0}

    filas = _filas(
        'estadio_db_test',
        'SELECT id_usuario FROM tareas_asignadas WHERE id_tarea = %s AND Estatus = 1',
        (id_tarea,),
    )
    assert [f['id_usuario'] for f in filas] == [activo.id]
    assert _total(
        'seguridad_test',
        'SELECT COUNT(*) total FROM notificaciones WHERE usuario_id = %s',
        (inactivo.id,),
    ) == 0


def test_pl_tar_int_03_dedupe_combinado_una_notificacion_por_usuario(
    app, client, superadmin, crear_usuario
):
    """ multi-select duplicado + campo legacy + departamento = una sola fila por usuario. """
    departamento = f'Pipeline {uuid.uuid4().hex[:6]}'
    usuarios = [crear_usuario(), crear_usuario()]
    gestor = UsuarioModel()
    for usuario in usuarios:
        assert gestor.modificar(usuario.id, {'departamento': departamento}) is not None

    id_tarea = _crear_tarea(superadmin.id)
    u1, u2 = usuarios
    respuesta = client.post('/gestion-tarea/', data={
        'asignar': 'true',
        'id_tarea': str(id_tarea),
        'id_usuarios': [str(u1.id), str(u1.id), str(u2.id)],
        'id_usuario': str(u1.id),
        'departamento': departamento,
    })
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert cuerpo['success'] is True
    assert cuerpo['asignados'] == 2
    assert cuerpo['omitidos'] == 0

    filas = _filas(
        'estadio_db_test',
        'SELECT id_usuario FROM tareas_asignadas WHERE id_tarea = %s AND Estatus = 1',
        (id_tarea,),
    )
    assert sorted(f['id_usuario'] for f in filas) == sorted([u1.id, u2.id])
    for usuario in usuarios:
        assert _total(
            'seguridad_test',
            "SELECT COUNT(*) total FROM notificaciones "
            "WHERE usuario_id = %s AND tipo = 'tarea_asignada'",
            (usuario.id,),
        ) == 1
