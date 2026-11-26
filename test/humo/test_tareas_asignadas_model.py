import uuid
import pytest
from flask import g

from app.database import Database
from app.model.tarea_model import TareasAsignadasModel


def _cambiar_actor(client, login_fn, usuario):
    client.get("/auth/logout")
    g.pop("_login_user", None)
    login_fn(usuario)
    g.pop("_login_user", None)


@pytest.fixture()
def tarea_humo(app):
    """Crea una tarea mínima para smoke test y borra sus rastros al terminar."""
    creadas = []

    def _crear(id_creador=None):
        nombre = f"Humo Tarea {uuid.uuid4().hex[:6]}"
        with Database.get_connection("estadio_db_test").cursor() as cur:
            cur.execute(
                """INSERT INTO tareas (Nombre_Tarea, Instruccion, id_usuario_creador, Estatus)
                   VALUES (%s, %s, %s, 1)""",
                (nombre, "Prueba de humo", id_creador),
            )
            tarea_id = cur.lastrowid
            cur.execute("SELECT * FROM tareas WHERE id_tarea = %s", (tarea_id,))
            row = cur.fetchone()
        creadas.append(tarea_id)
        return row

    yield _crear

    with Database.get_connection("estadio_db_test").cursor() as cur:
        for tid in creadas:
            cur.execute("DELETE FROM tareas_asignadas WHERE id_tarea = %s", (tid,))
            cur.execute("DELETE FROM tareas WHERE id_tarea = %s", (tid,))


def test_humo_flujo_basico_tareas_asignadas(
    app, client, login, crear_usuario, tarea_humo
):
    """Smoke test: asignar, listar en mis-tareas y completar sin errores 5xx."""
    creador = crear_usuario(rol="Superadmin")
    asignado = crear_usuario(rol="Superadmin")
    tarea = tarea_humo(id_creador=creador.id)

    try:
        # 1. Asignar tarea vía POST /gestion-tarea/
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
        assert resp_asig.get_json().get("success") is True

        # 2. Verificar que el asignado puede cargar /gestion-tarea/mis-tareas
        _cambiar_actor(client, login, asignado)
        resp_mis = client.get("/gestion-tarea/mis-tareas")
        assert resp_mis.status_code == 200
        assert tarea["Nombre_Tarea"].encode("utf-8") in resp_mis.data

        # 3. Completar la asignación y confirmar estado 'Completada'
        asig = TareasAsignadasModel().consultar(
            id_tarea=tarea["id_tarea"], id_usuario=asignado.id
        )[0]
        resp_comp = client.post(
            "/gestion-tarea/completar",
            data={"id_asignacion": str(asig["id_asignacion"])},
            headers={"Accept": "application/json"},
        )
        assert resp_comp.status_code == 200
        assert resp_comp.get_json().get("success") is True

        actualizada = TareasAsignadasModel().obtener_por_id(asig["id_asignacion"])
        assert actualizada["Estado"] == "Completada"
    finally:
        with Database.get_connection("seguridad_test").cursor() as cur:
            cur.execute(
                "DELETE FROM notificaciones WHERE usuario_id IN (%s, %s)",
                (creador.id, asignado.id),
            )