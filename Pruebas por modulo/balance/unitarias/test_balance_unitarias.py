from app.model.balance_model import Pago


def test_valida_montos_positivos():
    assert Pago().validar_monto(1500.50) is True


def test_rechaza_montos_no_positivos():
    assert Pago().validar_monto(0) is False
    assert Pago().validar_monto(-10) is False
    assert Pago().validar_monto('abc') is False
