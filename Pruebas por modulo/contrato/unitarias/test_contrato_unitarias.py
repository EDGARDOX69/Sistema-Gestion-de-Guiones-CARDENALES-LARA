from datetime import date
from app.model.contrato_model import ContratoModel


def _modelo():
    modelo = ContratoModel()
    modelo.set_id_patrocinador(1)
    modelo.set_fecha_inicio(date(2026, 1, 1))
    modelo.set_fecha_fin(date(2026, 12, 31))
    modelo.set_tipo('1')
    modelo.set_monto_total(1000)
    return modelo


def test_contrato_valido():
    assert _modelo()._validar_datos_contrato() is True


def test_tipo_de_contrato_invalido():
    modelo = _modelo()
    try:
        modelo.set_tipo('9')
    except ValueError:
        return
    raise AssertionError('El tipo invalido fue aceptado')
