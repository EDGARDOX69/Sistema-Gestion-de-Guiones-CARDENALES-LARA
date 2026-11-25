from app.model.rol_model import MODULOS_DASHBOARD, MODULO_PERMISO_MAP


def test_modulos_del_dashboard():
    assert 'guion' in MODULOS_DASHBOARD
    assert 'balance' in MODULOS_DASHBOARD


def test_permiso_de_balance():
    assert MODULO_PERMISO_MAP['balance'] == 'balance.view'
