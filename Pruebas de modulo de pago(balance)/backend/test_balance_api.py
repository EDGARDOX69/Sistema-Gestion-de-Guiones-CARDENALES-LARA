# python -m pytest test/backend/test_balance_api.py -v

import pytest
from app.database import Database

def test_todas_las_apis_balance(client, app):
    """Prueba de Backend (API): Valida todos los endpoints GET y POST del módulo de balance."""
    
    # 1. Preparación de datos base en MySQL usando los nombres reales de tus columnas
    with app.app_context():
        db = Database.get_connection('estadio_db_test')
        with db.cursor() as cursor:
            # Insertamos en patrocinadores (columna real: nombre_empresa)
            cursor.execute("INSERT INTO patrocinadores (nombre_empresa) VALUES ('Sponsor API C.A.');")
            id_patrocinador = cursor.lastrowid
            
            # Insertamos en contrato (columnas reales: id_patrocinador, monto_total, estado)
            cursor.execute("""
                INSERT INTO contrato (id_patrocinador, monto_total, estado) 
                VALUES (%s, 5000.00, 1);
            """, (id_patrocinador,))
            id_contrato = cursor.lastrowid

            # Insertamos en pagos (columnas reales: id_contrato, monto, tipo_pago, referencia, fecha_pago, hora_pago, estado, fecha_registro)
            cursor.execute("""
                INSERT INTO pagos (id_contrato, monto, tipo_pago, referencia, fecha_pago, hora_pago, estado, fecha_registro) 
                VALUES (%s, 1000.00, 'Transferencia', 'REF-001', '2026-11-16', '10:00:00', 1, NOW());
            """, (id_contrato,))
            id_pago = cursor.lastrowid
        db.commit()

    # ---------------------------------------------------------
    # PRUEBA 1: Vista principal / Dashboard (GET /balance/)
    # ---------------------------------------------------------
    res_dashboard = client.get('/balance/')
    assert res_dashboard.status_code in [200, 302]

    # ---------------------------------------------------------
    # PRUEBA 2: API Resumen de contrato (GET /balance/api/contrato/<id>)
    # ---------------------------------------------------------
    res_contrato = client.get(f'/balance/api/contrato/{id_contrato}')
    assert res_contrato.status_code in [200, 302]
    if res_contrato.status_code == 200:
        assert res_contrato.is_json
        assert isinstance(res_contrato.get_json(), dict)

    # ---------------------------------------------------------
    # PRUEBA 3: API Detalle de pago (GET /balance/api/pago/<id>)
    # ---------------------------------------------------------
    res_pago = client.get(f'/balance/api/pago/{id_pago}')
    assert res_pago.status_code in [200, 302]
    if res_pago.status_code == 200:
        assert res_pago.is_json
        assert isinstance(res_pago.get_json(), dict)

    # ---------------------------------------------------------
    # PRUEBA 4: Estado de cuenta PDF (GET /balance/contrato/<id>/pdf)
    # ---------------------------------------------------------
    res_pdf = client.get(f'/balance/contrato/{id_contrato}/pdf')
    assert res_pdf.status_code in [200, 302]
    if res_pdf.status_code == 200:
        assert res_pdf.content_type == 'application/pdf'

    # ---------------------------------------------------------
    # PRUEBA 5: Registrar nuevo pago (POST /balance/registrar-pago)
    # ---------------------------------------------------------
    datos_nuevo_pago = {
        "id_contrato": id_contrato,
        "monto": 500.00,
        "tipo_pago": "Pago Móvil",
        "referencia": "REF-002",
        "fecha_pago": "2026-11-16",
        "hora_pago": "11:00:00",
        "descripcion": "Abono prueba API"
    }
    res_post = client.post('/balance/registrar-pago', data=datos_nuevo_pago)
    assert res_post.status_code in [200, 201, 302]