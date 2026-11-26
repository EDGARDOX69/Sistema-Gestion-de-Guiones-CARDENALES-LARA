# python -m pytest test/humo/test_balance_humo.py -v 

import pytest
from app.model.balance_model import Pago
from app.database import Database

def test_smoke_conexion_bd_test(app):
    """Humo 1: Verifica que la conexión directa a la BD de pruebas (estadio_db_test) esté activa."""
    with app.app_context():
        # Conectamos explícitamente a tu base de datos de pruebas
        db = Database.get_connection('estadio_db_test')
        with db.cursor() as cur:
            cur.execute("SELECT 1;")
            resultado = cur.fetchone()
        
        assert resultado is not None

        # Validamos también que el modelo responda sin lanzar excepciones
        modelo = Pago()
        contratos = modelo.obtener_contratos_activos()
        assert isinstance(contratos, list)

def test_smoke_rutas_principales_vivas(client):
    """Humo 2: Verifica que las rutas críticas del Blueprint /balance respondan sin error de servidor (500)."""
    rutas_criticas = [
        '/balance/',
        '/balance/api/contrato/1',
        '/balance/api/pago/1',
        '/balance/contrato/1/pdf'
    ]
    
    for ruta in rutas_criticas:
        response = client.get(ruta)
        # Aceptamos 200 (OK), 302 (redirige a login) o 404 controlado si el ID 1 no existe en estadio_db_test,
        # pero NUNCA un error fatal 500.
        assert response.status_code < 500, f"Fallo crítico 500 en la ruta {ruta}"

def test_smoke_endpoint_registro_activo(client):
    """Humo 3: Verifica que el endpoint POST de registro de pagos reciba peticiones sin colapsar."""
    response = client.post('/balance/registrar-pago', data={})
    assert response.status_code < 500, "El endpoint POST /balance/registrar-pago arrojó error interno 500"