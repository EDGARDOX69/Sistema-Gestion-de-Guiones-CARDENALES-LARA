import uuid
import pytest
from flask import g

from app.database import Database
from app.model.tarea_model import TareasAsignadasModel


def _reset_usuario_cache():
    """Limpia el usuario cacheado por Flask-Login al cambiar de actor.

    El app context del fixture _contexto sobrevive a los requests: sin esto,
    auth.login cree que ya hay sesión (redirige) y la vista sigue viendo al
    usuario anterior aunque la cookie de sesión ya cambió.
    """
    g.pop('_login_user', None)


@pytest.fixture()
def crear_tarea_base(app):
    """Inserta una tarea activa en estadio_db_test y la elimina al finalizar."""
    creados = []

    def _crear(nombre=None, instruccion="Instrucción de integración", id_creador=None):
        nombre_final = nombre or f"Tarea Integración {uuid.uuid4().hex[:8]}"
        with Database.get_connection("estadio_db_test").cursor() as cur:
            cur.execute(
                """INSERT INTO tareas (Nombre_Tarea, Instruccion, id_usuario_creador, Estatus)
                   VALUES (%s, %s, %s, 1)""",
                (nombre_final, instruccion, id_creador),
            )
            id_tarea = cur.lastrowid
            cur.execute("SELECT * FROM tareas WHERE id_tarea = %s", (id_tarea,))
            tarea = cur.fetchone()
        creados.append(id_tarea)
        return tarea

    yield _crear

    with Database.get_connection("estadio_db_test").cursor() as cur:
        for id_tarea in creados:
            cur.execute("DELETE FROM tareas_asignadas WHERE id_tarea = %s", (id_tarea,))
            cur.execute("DELETE FROM tareas WHERE id_tarea = %s", (id_tarea,))


def _limpiar_notificaciones_usuario(usuario_id):
    with Database.get_connection("seguridad_test").cursor() as cur:
        cur.execute("DELETE FROM notificaciones WHERE usuario_id = %s", (usuario_id,))


def test_integracion_modelo_asignar_duplicados_y_completar(
    app, crear_usuario, crear_tarea_base
):
    u1 = crear_usuario(rol="Superadmin")
    u2 = crear_usuario(rol="Superadmin")
    tarea = crear_tarea_base(nombre="Tarea Modelo Integración", id_creador=u1.id)
    modelo = TareasAsignadasModel()

    try:
        # 1. Asignación múltiple + omisión de duplicados
        asignados, omitidos = modelo.asignar_a_usuarios(
            tarea["id_tarea"], [u1.id, u2.id, u1.id], tarea["Nombre_Tarea"], u1.nombre
        )
        assert asignados == [u1.id, u2.id]
        assert omitidos == [u1.id]

        # Reintentar asignar a u1 debe omitirlo por duplicado activo
        asignados_2, omitidos_2 = modelo.asignar_a_usuarios(
            tarea["id_tarea"], [u1.id], tarea["Nombre_Tarea"], u1.nombre
        )
        assert asignados_2 == []
        assert omitidos_2 == [u1.id]

        # 2. Verificar consultas y conteo de pendientes
        assert modelo.contar_pendientes(u1.id) >= 1
        mis_tareas_u1 = modelo.obtener_por_usuario(u1.id)
        assert any(t["id_tarea"] == tarea["id_tarea"] for t in mis_tareas_u1)

        todas = modelo.consultar_todas()
        fila_u1 = next((f for f in todas if f["id_tarea"] == tarea["id_tarea"] and f["id_usuario"] == u1.id), None)
        assert fila_u1 is not None
        assert fila_u1["Estado"] == "Pendiente"
        assert fila_u1["usuario_nombre"] == u1.nombre

        # 3. Verificar notificación persistida en seguridad_test
        with Database.get_connection("seguridad_test").cursor() as cur:
            cur.execute(
                """SELECT * FROM notificaciones
                   WHERE usuario_id = %s AND tipo = 'tarea_asignada'
                   ORDER BY id DESC LIMIT 1""",
                (u1.id,),
            )
            notif = cur.fetchone()
        assert notif is not None
        assert tarea["Nombre_Tarea"] in notif["mensaje"]

        # 4. Completar asignación y comprobar actualización
        modelo.modificar_estado(fila_u1["id_asignacion"], "Completada")
        actualizada = modelo.obtener_por_id(fila_u1["id_asignacion"])
        assert actualizada["Estado"] == "Completada"
    finally:
        _limpiar_notificaciones_usuario(u1.id)
        _limpiar_notificaciones_usuario(u2.id)


def test_integracion_rutas_asignar_consultar_y_completar(
    app, client, login, crear_usuario, crear_tarea_base
):
    creador = crear_usuario(rol="Superadmin")
    asignado = crear_usuario(rol="Superadmin")
    tarea = crear_tarea_base(nombre="Tarea Ruta Integración", id_creador=creador.id)

    try:
        # 1. Creador asigna la tarea vía POST /gestion-tarea/
        login(creador)
        resp_asig = client.post(
            "/gestion-tarea/",
            data={
                "asignar": "true",
                "id_tarea": str(tarea["id_tarea"]),
                "id_usuarios": [str(asignado.id)],
            },
        )
        assert resp_asig.status_code == 200
        body_asig = resp_asig.get_json()
        assert body_asig["success"] is True
        assert body_asig["asignados"] == 1

        # 2. Consultar asignaciones desde seguimiento
        resp_seg = client.post("/gestion-tarea/consultar-asignaciones")
        assert resp_seg.status_code == 200
        filas = resp_seg.get_json()
        registro = next(
            (r for r in filas if r["id_tarea"] == tarea["id_tarea"] and r["id_usuario"] == asignado.id),
            None,
        )
        assert registro is not None
        assert registro["Estado"] == "Pendiente"

        # 3. Usuario asignado consulta /gestion-tarea/mis-tareas y completa vía /gestion-tarea/completar
        # auth.login redirige si current_user sigue autenticado: hay que cerrar
        # la sesión del creador y limpiar el caché de flask_login para cambiar de actor.
        client.get("/auth/logout")
        _reset_usuario_cache()
        login(asignado)
        _reset_usuario_cache()
        resp_mis = client.get("/gestion-tarea/mis-tareas")
        assert resp_mis.status_code == 200
        assert tarea["Nombre_Tarea"].encode("utf-8") in resp_mis.data

        resp_comp = client.post(
            "/gestion-tarea/completar",
            data={"id_asignacion": str(registro["id_asignacion"])},
            headers={"Accept": "application/json"},
        )
        assert resp_comp.status_code == 200
        assert resp_comp.get_json()["success"] is True

        # 4. Verificar estado en BD y notificación al creador
        asignacion_bd = TareasAsignadasModel().obtener_por_id(registro["id_asignacion"])
        assert asignacion_bd["Estado"] == "Completada"

        with Database.get_connection("seguridad_test").cursor() as cur:
            cur.execute(
                """SELECT * FROM notificaciones
                   WHERE usuario_id = %s AND tipo = 'tarea_completada'
                   ORDER BY id DESC LIMIT 1""",
                (creador.id,),
            )
            notif_comp = cur.fetchone()
        assert notif_comp is not None
        assert tarea["Nombre_Tarea"] in notif_comp["mensaje"]
    finally:
        _limpiar_notificaciones_usuario(creador.id)
        _limpiar_notificaciones_usuario(asignado.id)
