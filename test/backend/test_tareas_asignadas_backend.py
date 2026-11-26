import pytest
from flask import g

from app.database import Database
from app.model.auth_model import Usuario
from app.model.notificacion_model import NotificacionModel
from app.model.tarea_model import TareaModel, TareasAsignadasModel


def _cambiar_actor(client, login_fn, usuario):
    """Cambia el usuario autenticado en el cliente de pruebas y limpia caché."""
    client.get("/auth/logout")
    g.pop("_login_user", None)
    login_fn(usuario)
    g.pop("_login_user", None)


def _limpiar_notificaciones(usuario_ids):
    if not usuario_ids:
        return
    placeholders = ",".join(["%s"] * len(usuario_ids))
    with Database.get_connection("seguridad_test").cursor() as cur:
        cur.execute(
            f"DELETE FROM notificaciones WHERE usuario_id IN ({placeholders})",
            tuple(usuario_ids),
        )


@pytest.fixture()
def tarea_temporal(app):
    """Inserta una tarea activa en estadio_db_test y elimina registros al finalizar."""
    creadas = []

    def _crear(nombre="Tarea Backend Completa", instruccion="Instrucción de prueba", id_creador=None):
        with Database.get_connection("estadio_db_test").cursor() as cur:
            cur.execute(
                """INSERT INTO tareas (Nombre_Tarea, Instruccion, id_usuario_creador, Estatus)
                   VALUES (%s, %s, %s, 1)""",
                (nombre, instruccion, id_creador),
            )
            tarea_id = cur.lastrowid
            cur.execute("SELECT * FROM tareas WHERE id_tarea = %s", (tarea_id,))
            fila = cur.fetchone()
        creadas.append(tarea_id)
        return fila

    yield _crear

    with Database.get_connection("estadio_db_test").cursor() as cur:
        for tid in creadas:
            cur.execute("DELETE FROM tareas_asignadas WHERE id_tarea = %s", (tid,))
            cur.execute("DELETE FROM tareas WHERE id_tarea = %s", (tid,))

def test_backend_acceso_sin_sesion_redirige(client):  
    resp_mis = client.get("/gestion-tarea/mis-tareas")
    assert resp_mis.status_code in (302, 401)

    resp_cons = client.post("/gestion-tarea/consultar-asignaciones")
    assert resp_cons.status_code in (302, 401)

    resp_comp = client.post(
        "/gestion-tarea/completar",
        data={"id_asignacion": "1"},
        headers={"Accept": "application/json"},
    )
    assert resp_comp.status_code in (302, 401)

def test_backend_permisos_asignar_supervisar_y_completar_ajena(
    app, client, login, crear_usuario, tarea_temporal, monkeypatch
):
    u_sin_permiso = crear_usuario(rol="Superadmin")
    u_dueno = crear_usuario(rol="Superadmin")
    tarea = tarea_temporal(id_creador=u_dueno.id)

    try:
        # Asignación previa hecha por u_dueno
        login(u_dueno)
        r_asig = client.post(
            "/gestion-tarea/",
            data={
                "asignar": "true",
                "id_tarea": str(tarea["id_tarea"]),
                "id_usuarios": [str(u_dueno.id)],
            },
        )
        assert r_asig.status_code == 200
        asig = TareasAsignadasModel().consultar(
            id_tarea=tarea["id_tarea"], id_usuario=u_dueno.id
        )[0]

        # Cambiar a u_sin_permiso sin 'gestion_tarea.create' ni 'gestion_tarea.supervisar'.
        # El user_loader crea una instancia NUEVA en cada request, así que parchear
        # solo el objeto del fixture no surte efecto al ejecutar esta prueba aislada.
        _cambiar_actor(client, login, u_sin_permiso)
        monkeypatch.setattr(
            Usuario,
            "tiene_permiso",
            lambda self, perm: perm not in ("gestion_tarea.create", "gestion_tarea.supervisar"),
        )

        r_den_asig = client.post(
            "/gestion-tarea/",
            data={
                "asignar": "true",
                "id_tarea": str(tarea["id_tarea"]),
                "id_usuarios": [str(u_sin_permiso.id)],
            },
        )
        assert r_den_asig.status_code == 403
        assert "No tienes permiso" in r_den_asig.get_json().get("error", "")

        r_den_sup = client.post("/gestion-tarea/consultar-asignaciones")
        assert r_den_sup.status_code == 403
        assert r_den_sup.get_json().get("error") == "Sin permiso"

        r_den_comp = client.post(
            "/gestion-tarea/completar",
            data={"id_asignacion": str(asig["id_asignacion"])},
            headers={"Accept": "application/json"},
        )
        assert r_den_comp.status_code == 403
        assert "Sin permiso" in r_den_comp.get_json().get("error", "")
    finally:
        _limpiar_notificaciones([u_sin_permiso.id, u_dueno.id])

def test_backend_validaciones_entradas_y_400_404(
    app, client, login, crear_usuario, tarea_temporal
):
    usuario = crear_usuario(rol="Superadmin")
    tarea = tarea_temporal(id_creador=usuario.id)
    login(usuario)

    try:
        # Sin id_tarea
        r_sin_tarea = client.post(
            "/gestion-tarea/",
            data={"asignar": "true", "id_usuarios": [str(usuario.id)]},
        )
        assert r_sin_tarea.status_code == 200
        assert r_sin_tarea.get_json() == {
            "success": False,
            "error": "Selecciona una tarea",
        }

        # Sin destinatarios
        r_sin_dest = client.post(
            "/gestion-tarea/",
            data={"asignar": "true", "id_tarea": str(tarea["id_tarea"])},
        )
        assert r_sin_dest.status_code == 200
        assert r_sin_dest.get_json() == {
            "success": False,
            "error": "Selecciona al menos un empleado o un departamento",
        }

        # Tarea inexistente
        r_no_tarea = client.post(
            "/gestion-tarea/",
            data={
                "asignar": "true",
                "id_tarea": "99999999",
                "id_usuarios": [str(usuario.id)],
            },
        )
        assert r_no_tarea.status_code == 200
        assert r_no_tarea.get_json() == {
            "success": False,
            "error": "Tarea no encontrada",
        }

        # Completar sin id_asignacion (JSON -> 400)
        r_faltante = client.post(
            "/gestion-tarea/completar",
            data={},
            headers={"Accept": "application/json"},
        )
        assert r_faltante.status_code == 400
        assert r_faltante.get_json() == {"error": "Asignación faltante"}

        # Completar asignación inexistente (JSON -> 404)
        r_no_asig = client.post(
            "/gestion-tarea/completar",
            data={"id_asignacion": "99999999"},
            headers={"Accept": "application/json"},
        )
        assert r_no_asig.status_code == 404
        assert r_no_asig.get_json() == {"error": "Asignación no encontrada"}
    finally:
        _limpiar_notificaciones([usuario.id])

def test_backend_deduplicacion_duplicados_y_autocompletar_sin_autonotificacion(
    app, client, login, crear_usuario, tarea_temporal, monkeypatch
):
    creador = crear_usuario(rol="Superadmin")
    u2 = crear_usuario(rol="Superadmin")
    tarea = tarea_temporal(nombre="Tarea Reglas Backend", id_creador=creador.id)

    try:
        login(creador)

        # Enviar id_usuarios duplicado + id_usuario repetido -> debe asignar 1 vez a creador y 1 vez a u2
        r_asig1 = client.post(
            "/gestion-tarea/",
            data={
                "asignar": "true",
                "id_tarea": str(tarea["id_tarea"]),
                "id_usuarios": [str(creador.id), str(u2.id), str(u2.id)],
                "id_usuario": str(creador.id),
            },
        )
        assert r_asig1.status_code == 200
        d1 = r_asig1.get_json()
        assert d1["success"] is True
        assert d1["asignados"] == 2
        assert d1["omitidos"] == 0

        # Reenviar a los mismos usuarios -> omite ambos duplicados activos
        r_asig2 = client.post(
            "/gestion-tarea/",
            data={
                "asignar": "true",
                "id_tarea": str(tarea["id_tarea"]),
                "id_usuarios": [str(creador.id), str(u2.id)],
            },
        )
        assert r_asig2.status_code == 200
        d2 = r_asig2.get_json()
        assert d2["success"] is True
        assert d2["asignados"] == 0
        assert d2["omitidos"] == 2

        # Creador completa su propia asignación: no debe generar notificación 'tarea_completada' para sí mismo
        asig_creador = TareasAsignadasModel().consultar(
            id_tarea=tarea["id_tarea"], id_usuario=creador.id
        )[0]
        notifs_creadas = []
        monkeypatch.setattr(
            NotificacionModel,
            "crear",
            lambda self, *args, **kwargs: notifs_creadas.append(args) or True,
        )

        r_comp = client.post(
            "/gestion-tarea/completar",
            data={"id_asignacion": str(asig_creador["id_asignacion"])},
            headers={"Accept": "application/json"},
        )
        assert r_comp.status_code == 200
        assert r_comp.get_json() == {"success": True, "mensaje": "Tarea completada"}
        assert notifs_creadas == []

        actualizada = TareasAsignadasModel().obtener_por_id(asig_creador["id_asignacion"])
        assert actualizada["Estado"] == "Completada"
    finally:
        _limpiar_notificaciones([creador.id, u2.id])

def test_backend_contratos_consultar_asignaciones_y_redirect_formulario(
    app, client, login, crear_usuario, tarea_temporal
):
    creador = crear_usuario(rol="Superadmin")
    asignado = crear_usuario(rol="Superadmin")
    tarea = tarea_temporal(nombre="Tarea Contrato JSON", id_creador=creador.id)

    try:
        login(creador)
        r_asig = client.post(
            "/gestion-tarea/",
            data={
                "asignar": "true",
                "id_tarea": str(tarea["id_tarea"]),
                "id_usuarios": [str(asignado.id)],
            },
        )
        assert r_asig.status_code == 200

        # Contrato de POST /gestion-tarea/consultar-asignaciones
        r_cons = client.post("/gestion-tarea/consultar-asignaciones")
        assert r_cons.status_code == 200
        filas = r_cons.get_json()
        assert isinstance(filas, list)
        item = next(
            (x for x in filas if x["id_tarea"] == tarea["id_tarea"] and x["id_usuario"] == asignado.id),
            None,
        )
        assert item is not None
        for campo in (
            "id_asignacion",
            "id_tarea",
            "id_usuario",
            "Estado",
            "Nombre_Tarea",
            "Instruccion",
            "usuario_nombre",
            "usuario_cedula",
            "fecha_asignacion_tarea",
        ):
            assert campo in item

        # Envío nativo de formulario (sin Accept: application/json) -> redirección 302
        _cambiar_actor(client, login, asignado)
        r_form = client.post(
            "/gestion-tarea/completar",
            data={"id_asignacion": str(item["id_asignacion"])},
        )
        assert r_form.status_code in (302, 303)
        assert "/gestion-tarea/mis-tareas" in r_form.headers.get("Location", "")
    finally:
        _limpiar_notificaciones([creador.id, asignado.id])

def test_backend_fallo_modelo_devuelve_error_controlado(
    app, client, login, crear_usuario, tarea_temporal, monkeypatch
):
    usuario = crear_usuario(rol="Superadmin")
    tarea = tarea_temporal(id_creador=usuario.id)
    login(usuario)

    monkeypatch.setattr(
        TareasAsignadasModel,
        "asignar_a_usuarios",
        lambda self, *args, **kwargs: (None, None),
    )

    resp = client.post(
        "/gestion-tarea/",
        data={
            "asignar": "true",
            "id_tarea": str(tarea["id_tarea"]),
            "id_usuarios": [str(usuario.id)],
        },
    )
    assert resp.status_code == 200
    assert resp.get_json() == {
        "success": False,
        "error": "Error al asignar tarea",
    }