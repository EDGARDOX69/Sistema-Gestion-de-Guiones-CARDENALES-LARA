# python -m pytest test/integracion/test_premio_integracion.py -v 

import pytest
from app.model.premio_model import PremioModel

@pytest.fixture
def modelo_test():
    modelo = PremioModel()
    modelo.db_name = "estadio_db_test"
    return modelo

def test_integracion_ciclo_crud_y_entrega_premio(modelo_test):
    # 1. Registrar premio en BD de pruebas
    modelo_test.set_nombre("Premio Integración Test")
    modelo_test.set_id_patrocinador(1)
    modelo_test.set_descripcion("Prueba de integración MySQL")
    modelo_test.set_cantidad(3)
    modelo_test.set_foto("default-premio.png")
    registrado = modelo_test.confirmar_registro()
    assert registrado is True


    pendientes = modelo_test.obtener_premios_pendientes()
    creado = next((p for p in pendientes if p["nombre"] == "Premio Integración Test"), None)
    assert creado is not None
    premio_id = creado["id"]

    # 3. Entregar parcialmente (1 de 3) y verificar que sigue pendiente
    entregado_parcial = modelo_test.entregar(
        premio_id=premio_id, id_patrocinador=1,
        descripcion="Entrega parcial test", entregado_por=1, cantidad_entregar=1
    )
    assert entregado_parcial is True
    actualizado = modelo_test.obtener_para_api(premio_id)
    assert actualizado["cantidad_entregada"] == 1

    # 4. Eliminación lógica (soft-delete) para limpiar entorno de pruebas
    eliminado = modelo_test.confirmar_eliminacion(premio_id)
    assert eliminado is True
    assert modelo_test.obtener_para_api(premio_id) is None
