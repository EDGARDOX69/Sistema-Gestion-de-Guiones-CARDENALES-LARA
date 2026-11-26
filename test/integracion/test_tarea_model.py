
import pytest

from app.database import Database
from app.model.tarea_model import TareaModel


@pytest.fixture
def contexto_bd(app):
    """
    Usa la app de pruebas, configurada para conectar solo con *_test.
    """
    with app.app_context():
        yield


def test_ciclo_completo_tarea(contexto_bd):
    # El creador debe existir en la copia de prueba de seguridad.
    with Database.get_connection("seguridad_test").cursor() as cur:
        cur.execute("SELECT id FROM usuarios WHERE activo = 1 ORDER BY id LIMIT 1")
        usuario = cur.fetchone()

    if not usuario:
        pytest.skip("No hay usuarios activos en la base de datos seguridad_test.")

    usuario_id = usuario["id"]

    modelo = TareaModel()

    tarea_id = None

    try:
        # --------------------------------
        # 1. REGISTRAR
        # --------------------------------

        modelo.set_nombre_tarea("Tarea de prueba automatizada")
        modelo.set_instruccion(
            "Esta tarea fue creada mediante una prueba de integración."
        )
        modelo.set_id_usuario_creador(int(usuario_id))

        resultado = modelo.confirmar_registro()

        assert resultado, (
            f"No se pudo registrar la tarea. Errores: "
            f"{modelo.get_errores()}"
        )


        id_tarea = resultado

        # --------------------------------
        # 2. CONSULTAR
        # --------------------------------

        tarea = modelo.obtener_por_id(id_tarea)

        assert tarea is not None
        assert tarea["Nombre_Tarea"] == "Tarea de prueba automatizada"
        assert tarea["Estatus"] == 1

        # --------------------------------
        # 3. MODIFICAR
        # --------------------------------

        modelo.set_nombre_tarea("Tarea modificada por Pytest")
        modelo.set_instruccion(
            "La instrucción fue modificada correctamente por la prueba."
        )

        modificacion = modelo.confirmar_modificacion(id_tarea)

        assert modificacion is True

        tarea_modificada = modelo.obtener_por_id(id_tarea)

        assert tarea_modificada is not None
        assert tarea_modificada["Nombre_Tarea"] == (
            "Tarea modificada por Pytest"
        )

        # --------------------------------
        # 4. ELIMINAR LÓGICAMENTE
        # --------------------------------

        eliminacion = modelo.confirmar_eliminacion(id_tarea)

        assert eliminacion is not None

        # --------------------------------
        # 5. COMPROBAR ELIMINACIÓN
        # --------------------------------

        tarea_eliminada = modelo.obtener_por_id(id_tarea)

        assert tarea_eliminada is not None
        assert tarea_eliminada["Estatus"] == 0

        tareas_activas = modelo.consultar(activas=True)

        ids_activos = [t["id_tarea"] for t in tareas_activas]

        assert id_tarea not in ids_activos

    finally:
        # Si una aserción falla antes de la eliminación,
        # intentamos limpiar la tarea de prueba.
        if id_tarea is not None:
            tarea_actual = modelo.obtener_por_id(id_tarea)

            if tarea_actual and tarea_actual["Estatus"] == 1:
                modelo.confirmar_eliminacion(id_tarea)
