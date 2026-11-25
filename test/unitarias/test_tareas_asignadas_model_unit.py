"""
Pruebas unitarias para TareasAsignadasModel.

Estas pruebas aíslan el modelo de MySQL mediante FakeDB y FakeCursor.
Ajusta la importación de modulo_modelo si TareasAsignadasModel está
declarada en un módulo distinto de app.model.tarea_model.
"""

from contextlib import nullcontext
from unittest.mock import Mock

import pytest

import app.model.tarea_model as modulo_modelo
from app.model.tarea_model import TareasAsignadasModel
class FakeCursor:
    """Cursor simulado que registra SQL y devuelve resultados controlados."""

    def __init__(
        self,
        fetchone_results=None,
        fetchall_results=None,
        lastrowid=101,
        fail_on_execute=None,
    ):
        self.fetchone_results = list(fetchone_results or [])
        self.fetchall_results = list(fetchall_results or [])
        self.lastrowid = lastrowid
        self.fail_on_execute = fail_on_execute
        self.execute_count = 0
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, params=None):
        self.execute_count += 1
        self.executed.append((sql, params))
        if self.fail_on_execute == self.execute_count:
            raise RuntimeError("Error simulado de base de datos")

    def fetchone(self):
        if self.fetchone_results:
            return self.fetchone_results.pop(0)
        return None

    def fetchall(self):
        if self.fetchall_results:
            return self.fetchall_results.pop(0)
        return []


class FakeDB:
    """Conexión simulada. Devuelve el cursor configurado."""

    def __init__(self, cursor):
        self.fake_cursor = cursor

    def cursor(self):
        return self.fake_cursor

@pytest.fixture
def modelo_y_db(monkeypatch):
    cursor = FakeCursor()
    db = FakeDB(cursor)
    modelo = TareasAsignadasModel()

    monkeypatch.setattr(modelo, "_get_db", lambda: db)
    return modelo, cursor, db

def test_consultar_todas_las_asignaciones_activas(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    filas = [{"id_asignacion": 1}, {"id_asignacion": 2}]
    cursor.fetchall_results = [filas]

    resultado = modelo.consultar()

    assert resultado == filas
    sql, params = cursor.executed[0]
    assert "ta.Estatus = 1" in sql
    assert "ORDER BY ta.fecha_asignacion_tarea DESC" in sql
    assert params == []

def test_consultar_filtra_por_usuario(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    cursor.fetchall_results = [[{"id_usuario": 7}]]

    resultado = modelo.consultar(id_usuario=7)

    assert resultado == [{"id_usuario": 7}]
    sql, params = cursor.executed[0]
    assert "ta.id_usuario = %s" in sql
    assert params == [7]

def test_consultar_filtra_por_tarea(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    cursor.fetchall_results = [[{"id_tarea": 12}]]

    resultado = modelo.consultar(id_tarea=12)

    assert resultado == [{"id_tarea": 12}]
    sql, params = cursor.executed[0]
    assert "ta.id_tarea = %s" in sql
    assert params == [12]

def test_consultar_filtra_por_usuario_y_tarea(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    cursor.fetchall_results = [[{"id_usuario": 7, "id_tarea": 12}]]

    resultado = modelo.consultar(id_usuario=7, id_tarea=12)

    assert len(resultado) == 1
    sql, params = cursor.executed[0]
    assert "ta.id_usuario = %s" in sql
    assert "ta.id_tarea = %s" in sql
    assert params == [7, 12]

def test_consultar_devuelve_lista_vacia_si_hay_error(modelo_y_db, monkeypatch):
    modelo, _, _ = modelo_y_db
    monkeypatch.setattr(
        modelo, "_get_db",
        lambda: (_ for _ in ()).throw(RuntimeError("conexión fallida"))
    )

    assert modelo.consultar() == []

def test_obtener_por_id_devuelve_asignacion(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    asignacion = {"id_asignacion": 25, "id_usuario": 7}
    cursor.fetchone_results = [asignacion]

    resultado = modelo.obtener_por_id(25)

    assert resultado == asignacion
    sql, params = cursor.executed[0]
    assert "WHERE ta.id_asignacion = %s" in sql
    assert params == (25,)

def test_obtener_por_id_devuelve_none_si_no_existe(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    cursor.fetchone_results = [None]

    assert modelo.obtener_por_id(999) is None

def test_obtener_por_id_devuelve_none_si_hay_error(modelo_y_db, monkeypatch):
    modelo, _, _ = modelo_y_db
    monkeypatch.setattr(
        modelo, "_get_db",
        lambda: (_ for _ in ()).throw(RuntimeError("conexión fallida"))
    )

    assert modelo.obtener_por_id(25) is None

def test_obtener_por_usuario_devuelve_asignaciones_activas(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    filas = [{"id_asignacion": 3, "id_usuario": 7}]
    cursor.fetchall_results = [filas]

    resultado = modelo.obtener_por_usuario(7)

    assert resultado == filas
    sql, params = cursor.executed[0]
    assert "ta.id_usuario = %s" in sql
    assert "ta.Estatus = 1" in sql
    assert "t.Estatus = 1" in sql
    assert params == (7,)

def test_obtener_por_usuario_devuelve_lista_vacia_si_hay_error(modelo_y_db, monkeypatch):
    modelo, _, _ = modelo_y_db
    monkeypatch.setattr(
        modelo, "_get_db",
        lambda: (_ for _ in ()).throw(RuntimeError("conexión fallida"))
    )

    assert modelo.obtener_por_usuario(7) == []

def test_registrar_asignacion_correctamente(modelo_y_db, monkeypatch):
    modelo, cursor, _ = modelo_y_db
    asignacion = {"id_asignacion": 101, "id_tarea": 12, "id_usuario": 7}
    cursor.fetchone_results = [asignacion]
    buscar = Mock(return_value=asignacion)
    monkeypatch.setattr(modelo, "obtener_por_id", buscar)

    resultado = modelo.registrar({
        "id_tarea": 12,
        "id_usuario": 7,
    })

    assert resultado == asignacion
    sql, params = cursor.executed[0]
    assert "INSERT INTO tareas_asignadas" in sql
    assert params[0:3] == (12, 7, "Pendiente")
    buscar.assert_called_once_with(101)

def test_registrar_usa_estado_y_fecha_personalizados(modelo_y_db, monkeypatch):
    modelo, cursor, _ = modelo_y_db
    asignacion = {"id_asignacion": 101}
    monkeypatch.setattr(modelo, "obtener_por_id", Mock(return_value=asignacion))
    fecha = "2026-01-15 10:30:00"

    resultado = modelo.registrar({
        "id_tarea": 12,
        "id_usuario": 7,
        "Estado": "En progreso",
        "fecha_asignacion_tarea": fecha,
    })

    assert resultado == asignacion
    _, params = cursor.executed[0]
    assert params == (12, 7, "En progreso", fecha)

def test_registrar_devuelve_none_si_hay_error(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    cursor.fail_on_execute = 1

    resultado = modelo.registrar({"id_tarea": 12, "id_usuario": 7})

    assert resultado is None

def test_asignar_a_usuarios_asigna_y_omite_duplicados(monkeypatch):
    # Usuario 7 no está duplicado; usuario 8 ya tiene una asignación activa.
    cursor = FakeCursor(fetchone_results=[None, {"id_asignacion": 55}])
    db = FakeDB(cursor)
    modelo = TareasAsignadasModel()

    monkeypatch.setattr(modelo, "_get_db", lambda: db)
    monkeypatch.setattr(modulo_modelo, "transaction", lambda nombre: nullcontext())
    monkeypatch.setitem(
        modulo_modelo.DATABASE_CONFIG,
        "seguridad",
        {"database": "seguridad_test"},
    )

    asignados, omitidos = modelo.asignar_a_usuarios(
        12, [7, 8], "Preparar informe", "Coordinador"
    )

    assert asignados == [7]
    assert omitidos == [8]
    assert cursor.execute_count == 4
    assert any("INSERT INTO tareas_asignadas" in sql for sql, _ in cursor.executed)
    assert any("INSERT INTO seguridad_test.notificaciones" in sql for sql, _ in cursor.executed)

def test_asignar_a_usuarios_devuelve_listas_vacias_si_todos_son_duplicados(monkeypatch):
    cursor = FakeCursor(fetchone_results=[
        {"id_asignacion": 20},
        {"id_asignacion": 21},
    ])
    modelo = TareasAsignadasModel()

    monkeypatch.setattr(modelo, "_get_db", lambda: FakeDB(cursor))
    monkeypatch.setattr(modulo_modelo, "transaction", lambda nombre: nullcontext())
    monkeypatch.setitem(
        modulo_modelo.DATABASE_CONFIG,
        "seguridad",
        {"database": "seguridad_test"},
    )

    asignados, omitidos = modelo.asignar_a_usuarios(
        12, [7, 8], "Preparar informe", "Coordinador"
    )

    assert asignados == []
    assert omitidos == [7, 8]
    assert cursor.execute_count == 2

def test_asignar_a_usuarios_devuelve_none_none_si_hay_error(monkeypatch):
    cursor = FakeCursor(fail_on_execute=1)
    modelo = TareasAsignadasModel()

    monkeypatch.setattr(modelo, "_get_db", lambda: FakeDB(cursor))
    monkeypatch.setattr(modulo_modelo, "transaction", lambda nombre: nullcontext())
    monkeypatch.setitem(
        modulo_modelo.DATABASE_CONFIG,
        "seguridad",
        {"database": "seguridad_test"},
    )

    assert modelo.asignar_a_usuarios(
        12, [7], "Preparar informe", "Coordinador"
    ) == (None, None)

def test_modificar_estado_ejecuta_update(modelo_y_db):
    modelo, cursor, _ = modelo_y_db

    resultado = modelo.modificar_estado(25, "Completada")

    assert resultado is None  # El método no retorna un valor explícito.
    sql, params = cursor.executed[0]
    assert "UPDATE tareas_asignadas SET Estado = %s" in sql
    assert params == ("Completada", 25)

def test_consultar_todas_devuelve_registros(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    filas = [{"id_asignacion": 1, "usuario_nombre": "Usuario de prueba"}]
    cursor.fetchall_results = [filas]

    resultado = modelo.consultar_todas()

    assert resultado == filas
    sql, _ = cursor.executed[0]
    esquema_seg = modulo_modelo.DATABASE_CONFIG['seguridad']['database']
    assert f"JOIN {esquema_seg}.usuarios u" in sql
    assert "ta.Estatus = 1 AND t.Estatus = 1" in sql

def test_contar_pendientes_devuelve_total(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    cursor.fetchone_results = [{"total": 4}]

    resultado = modelo.contar_pendientes(7)

    assert resultado == 4
    sql, params = cursor.executed[0]
    assert "ta.Estado != 'Completada'" in sql
    assert params == (7,)

def test_contar_pendientes_devuelve_cero_si_no_hay_fila(modelo_y_db):
    modelo, cursor, _ = modelo_y_db
    cursor.fetchone_results = [None]

    assert modelo.contar_pendientes(7) == 0

def test_contar_pendientes_devuelve_cero_si_hay_error(modelo_y_db, monkeypatch):
    modelo, _, _ = modelo_y_db
    monkeypatch.setattr(
        modelo, "_get_db",
        lambda: (_ for _ in ()).throw(RuntimeError("conexión fallida"))
    )

    assert modelo.contar_pendientes(7) == 0
