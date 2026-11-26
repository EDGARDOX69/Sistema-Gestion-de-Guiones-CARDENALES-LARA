# python -m pytest test/backend/test_premio_backend.py -v

import pytest
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["LOGIN_DISABLED"] = True
    with app.test_client() as client:
        yield client

def test_backend_consultar_premios_json(client):
    with patch("app.helpers.decorators.current_user") as mock_dec_user, \
         patch("app.controller.premio_controller.PremioModel") as MockModel:
        mock_dec_user.is_authenticated = True
        mock_dec_user.tiene_permiso.return_value = True

        instancia = MockModel.return_value
        instancia.obtener_premios_pendientes.return_value = [
            {"id": 1, "nombre": "Balón", "descripcion": "Desc", "estado": "pendiente",
             "patrocinador_nombre": "Polar", "id_patrocinador": 1, "foto": "default-premio.png",
             "fecha_creacion": "2026-11-18", "cantidad": 10, "cantidad_entregada": 2}
        ]
        instancia.obtener_premios_entregados.return_value = []

        resp = client.post("/premio/", data={"accion": "consultar"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "pendientes" in data
        assert "entregados" in data


def test_backend_accion_no_reconocida_retorna_400(client):
    with patch("app.helpers.decorators.current_user") as mock_dec_user:
        mock_dec_user.is_authenticated = True
        mock_dec_user.tiene_permiso.return_value = True

        resp = client.post("/premio/", data={"accion": "accion_inexistente"})
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "Accion no reconocida"


def test_backend_entregar_cantidad_invalida_retorna_400(client):
    with patch("app.helpers.decorators.current_user") as mock_dec_user, \
         patch("app.controller.premio_controller.current_user") as mock_ctrl_user:
        mock_dec_user.is_authenticated = True
        mock_dec_user.tiene_permiso.return_value = True
        mock_ctrl_user.is_authenticated = True
        mock_ctrl_user.tiene_permiso.return_value = True

        resp = client.post("/premio/", data={
            "accion": "entregar",
            "id_premio": "1",
            "cantidad_entregar": "abc",
            "id_patrocinador": "1"
        })
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "Cantidad o patrocinador inválido"