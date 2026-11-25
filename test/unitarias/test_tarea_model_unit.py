"""
Pruebas unitarias para TareaModel.

Estas pruebas NO se conectan a MySQL. Simulan la conexión y el cursor
para comprobar el comportamiento del modelo de forma aislada.

Ejecutar desde la raíz del proyecto:
    pytest tests/unit/test_tarea_model_unit.py -v -s
"""

import pytest

from app.model.tarea_model import TareaModel


class FakeCursor:
    """Cursor simulado que registra las consultas ejecutadas."""

    def __init__(self, lastrowid=1, fetchone_result=None, fetchall_result=None):
        self.lastrowid = lastrowid
        self.fetchone_result = fetchone_result
        self.fetchall_result = fetchall_result if fetchall_result is not None else []
        self.queries = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.closed = True
        return False

    def execute(self, sql, params=None):
        self.queries.append((sql, params))

    def fetchone(self):
        return self.fetchone_result

    def fetchall(self):
        return self.fetchall_result


class FakeDB:
    """Conexión simulada que entrega un cursor falso."""

    def __init__(self, cursor=None):
        self.fake_cursor = cursor or FakeCursor()
        self.cursor_calls = 0

    def cursor(self):
        self.cursor_calls += 1
        return self.fake_cursor


@pytest.fixture
def modelo():
    return TareaModel()


def conectar_db_falsa(monkeypatch, modelo, db_falsa):
    """Reemplaza _get_db para evitar cualquier conexión real."""
    monkeypatch.setattr(modelo, "_get_db", lambda: db_falsa)


# ---------------------------------------------------------------------
# Validaciones y registro
# ---------------------------------------------------------------------

def test_validar_datos_rechaza_nombre_vacio(modelo):
    modelo.set_nombre_tarea("")
    modelo.set_instruccion("Esta es una instruccion suficientemente larga")

    assert modelo._validar_datos_tarea() is False
    assert modelo.tiene_errores()


def test_validar_datos_rechaza_nombre_demasiado_corto(modelo):
    modelo.set_nombre_tarea("AB")
    modelo.set_instruccion("Esta es una instruccion suficientemente larga")

    assert modelo._validar_datos_tarea() is False
    assert modelo.tiene_errores()


def test_validar_datos_rechaza_instruccion_demasiado_corta(modelo):
    modelo.set_nombre_tarea("Preparar informe")
    modelo.set_instruccion("Corta")

    assert modelo._validar_datos_tarea() is False
    assert modelo.tiene_errores()


def test_validar_datos_acepta_datos_correctos(modelo):
    modelo.set_nombre_tarea("Preparar informe")
    modelo.set_instruccion("Redactar y entregar el informe solicitado")

    assert modelo._validar_datos_tarea() is True
    assert modelo.tiene_errores() is False


def test_confirmar_registro_no_accede_a_db_si_datos_invalidos(
    modelo, monkeypatch
):
    db_falsa = FakeDB()
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    modelo.set_nombre_tarea("")
    modelo.set_instruccion("Instruccion suficientemente larga")

    resultado = modelo.confirmar_registro()

    assert resultado is False
    assert db_falsa.cursor_calls == 0


def test_confirmar_registro_devuelve_id_generado(modelo, monkeypatch):
    cursor = FakeCursor(lastrowid=42)
    db_falsa = FakeDB(cursor)
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    modelo.set_nombre_tarea("Preparar informe")
    modelo.set_instruccion("Redactar y entregar el informe solicitado")
    modelo.set_id_usuario_creador(7)

    resultado = modelo.confirmar_registro()

    assert resultado == 42
    assert len(cursor.queries) == 1

    sql, params = cursor.queries[0]
    assert "INSERT INTO tareas" in sql
    assert params == (
        "Preparar informe",
        "Redactar y entregar el informe solicitado",
        7,
    )


def test_registrar_devuelve_none_si_ocurre_un_error(modelo, monkeypatch):
    def provocar_error():
        raise RuntimeError("Error simulado de conexión")

    monkeypatch.setattr(modelo, "_get_db", provocar_error)

    modelo.set_nombre_tarea("Preparar informe")
    modelo.set_instruccion("Redactar y entregar el informe solicitado")

    assert modelo._registrar() is None


# ---------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------

def test_consultar_solo_activas_agrega_filtro_estatus(modelo, monkeypatch):
    cursor = FakeCursor(fetchall_result=[{"id_tarea": 3}])
    db_falsa = FakeDB(cursor)
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    resultado = modelo.consultar()

    assert resultado == [{"id_tarea": 3}]
    sql, params = cursor.queries[0]
    assert "WHERE Estatus = 1" in sql
    assert "ORDER BY id_tarea DESC" in sql
    assert params == []


def test_consultar_todas_no_agrega_filtro_de_activas(modelo, monkeypatch):
    cursor = FakeCursor(fetchall_result=[
        {"id_tarea": 3},
        {"id_tarea": 2},
    ])
    db_falsa = FakeDB(cursor)
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    resultado = modelo.consultar(activas=False)

    assert len(resultado) == 2
    sql, _ = cursor.queries[0]
    assert "WHERE Estatus = 1" not in sql
    assert "ORDER BY id_tarea DESC" in sql


def test_consultar_devuelve_lista_vacia_si_hay_error(modelo, monkeypatch):
    def provocar_error():
        raise RuntimeError("Error simulado")

    monkeypatch.setattr(modelo, "_get_db", provocar_error)

    assert modelo.consultar() == []


def test_obtener_por_id_devuelve_tarea(modelo, monkeypatch):
    tarea = {"id_tarea": 15, "Nombre_Tarea": "Preparar informe"}
    cursor = FakeCursor(fetchone_result=tarea)
    db_falsa = FakeDB(cursor)
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    resultado = modelo.obtener_por_id(15)

    assert resultado == tarea
    sql, params = cursor.queries[0]
    assert "WHERE id_tarea = %s" in sql
    assert params == (15,)


def test_obtener_por_id_devuelve_none_si_hay_error(modelo, monkeypatch):
    def provocar_error():
        raise RuntimeError("Error simulado")

    monkeypatch.setattr(modelo, "_get_db", provocar_error)

    assert modelo.obtener_por_id(15) is None


# ---------------------------------------------------------------------
# Modificación
# ---------------------------------------------------------------------

def test_modificar_actualiza_solo_campos_permitidos(modelo, monkeypatch):
    tarea_actualizada = {
        "id_tarea": 15,
        "Nombre_Tarea": "Nuevo nombre",
    }
    cursor = FakeCursor(fetchone_result=tarea_actualizada)
    db_falsa = FakeDB(cursor)
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    resultado = modelo.modificar(
        15,
        {
            "Nombre_Tarea": "Nuevo nombre",
            "Estatus": 0,  # Este campo no está permitido por el método.
        },
    )

    assert resultado == tarea_actualizada
    assert len(cursor.queries) == 2

    update_sql, update_params = cursor.queries[0]
    assert "UPDATE tareas SET Nombre_Tarea = %s WHERE id_tarea = %s" == update_sql
    assert update_params == ["Nuevo nombre", 15]

    select_sql, select_params = cursor.queries[1]
    assert "SELECT * FROM tareas WHERE id_tarea = %s" in select_sql
    assert select_params == (15,)


def test_confirmar_modificacion_no_accede_a_db_si_datos_invalidos(
    modelo, monkeypatch
):
    db_falsa = FakeDB()
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    modelo.set_nombre_tarea("AB")
    modelo.set_instruccion("Instruccion suficientemente larga")

    resultado = modelo.confirmar_modificacion(15)

    assert resultado is False
    assert db_falsa.cursor_calls == 0


def test_confirmar_modificacion_devuelve_true_si_modifica(modelo, monkeypatch):
    tarea_actualizada = {
        "id_tarea": 15,
        "Nombre_Tarea": "Nuevo nombre",
        "Instruccion": "Instruccion nueva suficientemente larga",
    }
    cursor = FakeCursor(fetchone_result=tarea_actualizada)
    db_falsa = FakeDB(cursor)
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    modelo.set_nombre_tarea("Nuevo nombre")
    modelo.set_instruccion("Instruccion nueva suficientemente larga")

    resultado = modelo.confirmar_modificacion(15)

    assert resultado is True
    assert len(cursor.queries) == 2
    assert "UPDATE tareas SET" in cursor.queries[0][0]


# ---------------------------------------------------------------------
# Eliminación lógica
# ---------------------------------------------------------------------

def test_confirmar_eliminacion_cambia_estatus_si_tarea_existe(
    modelo, monkeypatch
):
    tarea = {"id_tarea": 15, "Nombre_Tarea": "Preparar informe"}
    cursor = FakeCursor(fetchone_result=tarea)
    db_falsa = FakeDB(cursor)
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    resultado = modelo.confirmar_eliminacion(15)

    assert resultado == tarea
    assert len(cursor.queries) == 2

    select_sql, select_params = cursor.queries[0]
    assert "SELECT * FROM tareas WHERE id_tarea = %s" in select_sql
    assert select_params == (15,)

    update_sql, update_params = cursor.queries[1]
    assert "UPDATE tareas SET Estatus = 0 WHERE id_tarea = %s" in update_sql
    assert update_params == (15,)


def test_confirmar_eliminacion_no_actualiza_si_tarea_no_existe(
    modelo, monkeypatch
):
    cursor = FakeCursor(fetchone_result=None)
    db_falsa = FakeDB(cursor)
    conectar_db_falsa(monkeypatch, modelo, db_falsa)

    resultado = modelo.confirmar_eliminacion(999)

    assert resultado is None
    assert len(cursor.queries) == 1
    assert "SELECT * FROM tareas" in cursor.queries[0][0]
    assert all("UPDATE tareas" not in sql for sql, _ in cursor.queries)
