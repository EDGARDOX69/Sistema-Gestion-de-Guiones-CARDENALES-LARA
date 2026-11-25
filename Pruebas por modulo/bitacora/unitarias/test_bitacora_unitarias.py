from app.model.bitacora_model import ActividadModel


def test_extraer_detalle_texto():
    assert ActividadModel()._extraer_detalle('Cambio aplicado') == 'Cambio aplicado'


def test_extraer_detalle_dict():
    resultado = ActividadModel()._extraer_detalle({'detalle': 'Cambio aplicado'})
    assert 'Cambio aplicado' in resultado
