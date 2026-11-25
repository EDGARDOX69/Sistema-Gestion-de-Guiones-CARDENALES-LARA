from app.helpers.reportes_utils import _ordenar_datos, _parsear_fecha


def test_parsear_formatos_de_fecha():
    assert _parsear_fecha('2026-01-15') is not None
    assert _parsear_fecha('15/01/2026') is not None
    assert _parsear_fecha('fecha-invalida') is None


def test_ordenar_datos_ascendente():
    filas = [{'valor': 2}, {'valor': 1}]
    assert [f['valor'] for f in _ordenar_datos(filas, 'valor')] == [1, 2]
