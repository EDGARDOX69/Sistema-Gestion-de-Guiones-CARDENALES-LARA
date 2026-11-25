"""
Pruebas de integración del módulo Gestión de Tareas.
Requiere MySQL real con las bases estadio_db y seguridad.

Ejecutar desde la raíz del proyecto:
    pytest tests/test_tareas_integracion.py -v -s

Estas pruebas crean datos identificables y eliminan únicamente los registros
creados por ellas. No utilizan TRUNCATE ni limpian tablas completas.
"""

import os
import uuid

import pytest
from flask import Flask

from app.database import Database
from app.model.tarea_model import TareaModel, TareasAsignadasModel


@pytest.fixture
def contexto_bd():
    """Abre un contexto Flask para que Database pueda utilizar flask.g."""
    app = Flask(__name__)
    Database.init_app(app)

    with app.app_context():
        yield


@pytest.fixture
def escenario(contexto_bd):
    """
    Crea una tarea de prueba y obtiene un usuario activo de seguridad. 
    Al finalizar, elimina solo asignaciones, notificaciones y tarea de este escenario.
    """
    sufijo = uuid.uuid4().hex[:10]
    nombre = f"TEST_INTEGRACION_{sufijo}"
    instruccion = f"Instruccion de prueba de integracion {sufijo}"
    asignaciones = TareasAsignadasModel()
    tarea_id = None

    db = Database.get_connection("estadio_db")
    db_seguridad = Database.get_connection("seguridad")

    # Seleccionar un usuario activo real, sin modificar sus datos.
    with db_seguridad.cursor() as cur:
        cur.execute(
            "SELECT id FROM usuarios WHERE activo = 1 ORDER BY id LIMIT 1"
        )
        usuario = cur.fetchone()

    if not usuario:
        pytest.skip("No hay usuarios activos en la base de datos seguridad.")

    usuario_id = usuario["id"]

    # Crear tarea mediante el modelo real.
    modelo = TareaModel()
    modelo.set_nombre_tarea(nombre)
    modelo.set_instruccion(instruccion)
    modelo.set_id_usuario_creador(int(usuario_id))
    tarea_id = modelo.confirmar_registro()

    if not tarea_id:
        pytest.fail(
            "No se pudo crear la tarea de prueba. "
            "Revisa la estructura de estadio_db.tareas y el resultado de confirmar_registro()."
        )

    datos = {
        "nombre": nombre,
        "instruccion": instruccion,
        "tarea_id": tarea_id,
        "usuario_id": usuario_id,
    }

    yield datos

    # Limpieza selectiva: primero notificaciones y asignaciones, luego la tarea.
    try:
        with db_seguridad.cursor() as cur:
            cur.execute(
                "DELETE FROM notificaciones WHERE mensaje LIKE %s",
                (f'%"{nombre}"%',),
            )

        with db.cursor() as cur:
            cur.execute(
                "DELETE FROM tareas_asignadas WHERE id_tarea = %s",
                (tarea_id,),
            )
            cur.execute(
                "DELETE FROM tareas WHERE id_tarea = %s",
                (tarea_id,),
            )
    except Exception as exc:
        pytest.fail(f"No se pudieron limpiar los datos de prueba: {exc}")


def test_registrar_y_consultar_tarea_en_mysql(contexto_bd):
    """Comprueba que TareaModel registre y recupere una tarea en MySQL."""
    sufijo = uuid.uuid4().hex[:10]
    nombre = f"TEST_REGISTRO_{sufijo}"
    instruccion = f"Instruccion de integracion {sufijo}"
    modelo = TareaModel()
    tarea_id = None

    try:
        modelo.set_nombre_tarea(nombre)
        modelo.set_instruccion(instruccion)
        modelo.set_id_usuario_creador(None)
        tarea_id = modelo.confirmar_registro()

        assert tarea_id is not None

        recuperada = modelo.obtener_por_id(tarea_id)
        assert recuperada is not None
        assert recuperada["Nombre_Tarea"] == nombre
        assert recuperada["Instruccion"] == instruccion
        assert int(recuperada["Estatus"]) == 1
    finally:
        if tarea_id is not None:
            db = Database.get_connection("estadio_db")
            with db.cursor() as cur:
                cur.execute(
                    "DELETE FROM tareas WHERE id_tarea = %s",
                    (tarea_id,),
                )


def test_registrar_y_consultar_asignacion(escenario):
    """Comprueba que una asignación se inserte y pueda recuperarse desde MySQL."""
    modelo = TareasAsignadasModel()

    asignacion = modelo.registrar({
        "id_tarea": escenario["tarea_id"],
        "id_usuario": escenario["usuario_id"],
    })

    assert asignacion is not None
    assert asignacion["id_tarea"] == escenario["tarea_id"]
    assert asignacion["id_usuario"] == escenario["usuario_id"]
    assert asignacion["Estado"] == "Pendiente"

    recuperada = modelo.obtener_por_id(asignacion["id_asignacion"])
    assert recuperada is not None
    assert recuperada["id_asignacion"] == asignacion["id_asignacion"]


def test_consultar_asignaciones_por_usuario_y_tarea(escenario):
    """Comprueba que los filtros de usuario y tarea devuelvan la asignación correcta."""
    modelo = TareasAsignadasModel()

    asignacion = modelo.registrar({
        "id_tarea": escenario["tarea_id"],
        "id_usuario": escenario["usuario_id"],
    })
    assert asignacion is not None

    por_usuario = modelo.consultar(id_usuario=escenario["usuario_id"])
    por_tarea = modelo.consultar(id_tarea=escenario["tarea_id"])
    por_ambos = modelo.consultar(
        id_usuario=escenario["usuario_id"],
        id_tarea=escenario["tarea_id"],
    )

    assert any(
        fila["id_asignacion"] == asignacion["id_asignacion"]
        for fila in por_usuario
    )
    assert any(
        fila["id_asignacion"] == asignacion["id_asignacion"]
        for fila in por_tarea
    )
    assert any(
        fila["id_asignacion"] == asignacion["id_asignacion"]
        for fila in por_ambos
    )


def test_obtener_tareas_asignadas_por_usuario(escenario):
    """Comprueba que obtener_por_usuario incluya la tarea asignada al usuario."""
    modelo = TareasAsignadasModel()

    asignacion = modelo.registrar({
        "id_tarea": escenario["tarea_id"],
        "id_usuario": escenario["usuario_id"],
    })
    assert asignacion is not None

    resultado = modelo.obtener_por_usuario(escenario["usuario_id"])

    assert any(
        fila["id_asignacion"] == asignacion["id_asignacion"]
        and fila["Nombre_Tarea"] == escenario["nombre"]
        and fila["Instruccion"] == escenario["instruccion"]
        for fila in resultado
    )


def test_modificar_estado_y_contar_pendientes(escenario):
    """Comprueba que el estado se actualice en MySQL y cambie el conteo de pendientes."""
    modelo = TareasAsignadasModel()

    asignacion = modelo.registrar({
        "id_tarea": escenario["tarea_id"],
        "id_usuario": escenario["usuario_id"],
        "Estado": "Pendiente",
    })
    assert asignacion is not None

    pendientes_antes = modelo.contar_pendientes(escenario["usuario_id"])
    assert pendientes_antes >= 1

    modelo.modificar_estado(asignacion["id_asignacion"], "Completada")

    recuperada = modelo.obtener_por_id(asignacion["id_asignacion"])
    assert recuperada is not None
    assert recuperada["Estado"] == "Completada"

    pendientes_despues = modelo.contar_pendientes(escenario["usuario_id"])
    assert pendientes_despues == pendientes_antes - 1


def test_asignar_a_usuarios_genera_notificacion(escenario):
    """Comprueba la escritura coordinada en estadio_db y seguridad."""
    modelo = TareasAsignadasModel()

    asignados, omitidos = modelo.asignar_a_usuarios(
        id_tarea=escenario["tarea_id"],
        ids_usuarios=[escenario["usuario_id"]],
        titulo_tarea=escenario["nombre"],
        asignador="Prueba de integracion",
    )

    assert asignados == [escenario["usuario_id"]]
    assert omitidos == []

    db_seguridad = Database.get_connection("seguridad")
    with db_seguridad.cursor() as cur:
        cur.execute(
            """
            SELECT id, usuario_id, tipo, titulo, mensaje, url, leida
            FROM notificaciones
            WHERE usuario_id = %s AND mensaje LIKE %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (escenario["usuario_id"], f'%"{escenario["nombre"]}"%'),
        )
        notificacion = cur.fetchone()

    assert notificacion is not None
    assert notificacion["tipo"] == "tarea_asignada"
    assert notificacion["titulo"] == "Nueva tarea asignada"
    assert notificacion["leida"] == 0


def test_asignar_a_usuarios_evitar_duplicado(escenario):
    """Comprueba que una segunda asignación activa se omita y no duplique la notificación."""
    modelo = TareasAsignadasModel()

    primera = modelo.asignar_a_usuarios(
        escenario["tarea_id"],
        [escenario["usuario_id"]],
        escenario["nombre"],
        "Prueba de integracion",
    )
    segunda = modelo.asignar_a_usuarios(
        escenario["tarea_id"],
        [escenario["usuario_id"]],
        escenario["nombre"],
        "Prueba de integracion",
    )

    assert primera == ([escenario["usuario_id"]], [])
    assert segunda == ([], [escenario["usuario_id"]])

    db = Database.get_connection("estadio_db")
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS total
            FROM tareas_asignadas
            WHERE id_tarea = %s AND id_usuario = %s AND Estatus = 1
            """,
            (escenario["tarea_id"], escenario["usuario_id"]),
        )
        cantidad = cur.fetchone()["total"]

    assert cantidad == 1


def test_consultar_todas_incluye_datos_relacionados(escenario):
    """Comprueba la consulta que une tareas_asignadas, tareas y seguridad.usuarios."""
    modelo = TareasAsignadasModel()

    asignacion = modelo.registrar({
        "id_tarea": escenario["tarea_id"],
        "id_usuario": escenario["usuario_id"],
    })
    assert asignacion is not None

    resultado = modelo.consultar_todas()

    assert any(
        fila["id_asignacion"] == asignacion["id_asignacion"]
        and fila["Nombre_Tarea"] == escenario["nombre"]
        for fila in resultado
    )
