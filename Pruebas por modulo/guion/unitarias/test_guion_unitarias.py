from app.model.guion_model import _parsear_duracion


def test_duracion_con_segundos():
    assert _parsear_duracion('1,30') == 90


def test_duracion_en_minutos():
    assert _parsear_duracion('2') == 120
    assert _parsear_duracion('') == 0
