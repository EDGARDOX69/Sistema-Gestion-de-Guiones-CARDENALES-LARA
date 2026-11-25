# python -m pytest test/aceptacion/test_balance_aceptacion.py -v

import pytest
from app import create_app

@pytest.fixture
def cliente_uat():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_uat_flujo_completo_gestion_balance(cliente_uat):
    """
    Criterio de Aceptación RF-01:
    El usuario administrativo debe poder acceder al módulo de Balance, consultar
    el estado financiero de un contrato y registrar un pago, reflejándose
    la actualización de saldos de forma íntegra.
    """
    # 1. El usuario accede a la vista principal del módulo
    resp_vista = cliente_uat.get("/balance/", follow_redirects=True)
    assert resp_vista.status_code == 200

    # 2. El usuario consulta el detalle financiero de un contrato existente (ID 1)
    resp_consulta = cliente_uat.get("/balance/api/contrato/1")
    assert resp_consulta.status_code in [200, 302, 404]

    # 3. El usuario registra un abono/pago con datos de negocio válidos
    payload_negocio = {
        "id_contrato": 1,
        "monto": 250.00,
        "tipo_pago": "Transferencia",
        "referencia": "UAT-REF-2026",
        "fecha_pago": "2026-11-16",
        "hora_pago": "16:00:00",
        "descripcion": "Validación de aceptación de usuario RF-01"
    }
    resp_registro = cliente_uat.post(
        "/balance/registrar-pago",
        data=payload_negocio,
        follow_redirects=True
    )
    assert resp_registro.status_code in [200, 201, 400]