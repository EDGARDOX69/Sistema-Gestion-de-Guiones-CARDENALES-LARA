from app.model.premio_model import PremioModel


def _modelo():
    modelo = PremioModel()
    modelo.set_nombre('Premio Prueba')
    modelo.set_id_patrocinador(1)
    return modelo


def test_premio_valido():
    assert _modelo()._validar_datos_premio() is True


def test_premio_sin_patrocinador_es_invalido():
    modelo = PremioModel()
    modelo.set_nombre('Premio Prueba')
    assert modelo._validar_datos_premio() is False
