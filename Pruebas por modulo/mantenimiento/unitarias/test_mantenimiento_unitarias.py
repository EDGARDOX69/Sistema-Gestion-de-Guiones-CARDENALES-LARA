from datetime import date
from app.model.mantenimiento_model import MantenimientoModel


def _modelo():
    modelo = MantenimientoModel()
    modelo.set_recurso_id(1)
    modelo.set_usuario_id(1)
    modelo.set_fecha_ingreso(date.today())
    modelo.set_diagnostico('Revisar conexion electrica')
    return modelo


def test_mantenimiento_valido():
    assert _modelo()._validar_datos_mantenimiento() is True


def test_mantenimiento_sin_diagnostico_es_invalido():
    modelo = _modelo()
    modelo.set_diagnostico('')
    assert modelo._validar_datos_mantenimiento() is False
