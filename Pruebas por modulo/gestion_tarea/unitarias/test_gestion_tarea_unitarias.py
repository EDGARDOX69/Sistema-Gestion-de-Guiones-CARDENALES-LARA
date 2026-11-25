from app.model.tarea_model import TareaModel


def _modelo():
    modelo = TareaModel()
    modelo.set_nombre_tarea('Revisar inventario')
    modelo.set_instruccion('Revisar los activos del palco')
    return modelo


def test_tarea_valida():
    assert _modelo()._validar_datos_tarea() is True


def test_tarea_con_instruccion_corta_es_invalida():
    modelo = TareaModel()
    modelo.set_nombre_tarea('Revisar')
    modelo.set_instruccion('Corta')
    assert modelo._validar_datos_tarea() is False
