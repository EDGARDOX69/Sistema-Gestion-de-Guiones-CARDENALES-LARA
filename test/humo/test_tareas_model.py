import pytest

def test_humo_tareas_sin_500(client):
    """Verifica que la ruta de tareas no arroje error 500 sin sesión activa."""
    resp = client.get("/gestion-tarea/")
    assert resp.status_code != 500
    assert resp.status_code in [ 302, 401, 403]


def test_humo_dashboard_tareas_carga(client, superadmin):
    """Verifica que la vista principal de tareas cargue correctamente con sesión."""
    response = client.get("/gestion-tarea/")
    assert response.status_code == 200
    assert b"total tareas" in response.data.lower()


def test_humo_consulta_basica_tareas(client, superadmin):
    """Verifica que el endpoint de consulta de tareas responda 200 y retorne una lista JSON."""
    resp = client.post("/gestion-tarea/", data={"consultar": "2"})
    assert resp.status_code == 200
    assert resp.is_json
    datos=resp.get_json()
    assert isinstance(datos, list)
    assert all(isinstance(tarea, dict) for tarea in datos)


