from app.model.inventario_model import InventarioModel


def _modelo():
    modelo = InventarioModel()
    modelo.set_nombre('Audifonos')
    modelo.set_id_tipo(1)
    return modelo


def test_recurso_valido():
    assert _modelo()._validar_datos_recurso() is True


def test_recurso_con_nombre_corto_es_invalido():
    modelo = _modelo()
    modelo.set_nombre('A')
    assert modelo._validar_datos_recurso() is False
