from app.model.reels_model import ReelModel


def test_nombre_de_reel_valido():
    assert ReelModel()._validar_nombre('Reel Institucional') is True


def test_nombre_de_reel_corto_es_invalido():
    assert ReelModel()._validar_nombre('A') is False
