# python -m pytest test/humo/test_premio_humo.py -v 

import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_humo_dashboard_premio_disponible(client):
    resp = client.get("/premio/", follow_redirects=True)
    assert resp.status_code == 200