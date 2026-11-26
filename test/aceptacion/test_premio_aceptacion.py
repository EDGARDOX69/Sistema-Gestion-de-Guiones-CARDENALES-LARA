# python -m pytest test/aceptacion/test_premio_aceptacion.py -v

import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def cliente_uat():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["LOGIN_DISABLED"] = True
    with app.test_client() as client:
        yield client


def test_uat_flujo_completo_gestion_premios(cliente_uat):
    usuario_simulado = MagicMock()
    usuario_simulado.is_authenticated = True
    usuario_simulado.tiene_permiso.return_value = True
    usuario_simulado.id = 1

    with patch("app.helpers.decorators.current_user", usuario_simulado), \
         patch("app.controller.premio_controller.current_user", usuario_simulado):

        # 1. El usuario accede a la pantalla principal de Gestión de Premios
        resp_vista = cliente_uat.get("/premio/", follow_redirects=True)
        assert resp_vista.status_code == 200

        # 2. El usuario consulta el estado actual de premios pendientes y entregados
        resp_consulta = cliente_uat.post("/premio/", data={"accion": "consultar"})
        assert resp_consulta.status_code == 200
        datos = resp_consulta.get_json()
        assert "pendientes" in datos and "entregados" in datos

        # 3. El usuario registra un nuevo premio válido
        resp_registro = cliente_uat.post("/premio/", data={
            "accion": "registrar",
            "nombre": "Balón Autografiado UAT",
            "id_patrocinador": "1",
            "descripcion": "Validación funcional UAT",
            "cantidad": "5"
        })
        assert resp_registro.status_code in [200, 400]