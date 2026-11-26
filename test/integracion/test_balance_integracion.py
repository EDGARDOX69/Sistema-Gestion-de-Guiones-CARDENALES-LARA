# # python -m pytest test/integracion/test_balance_integracion.py -v -s

import uuid
from app.model.balance_model import Pago
from app.database import Database


def test_registrar_y_calcular_pago_en_bd_de_prueba(app, monkeypatch):
    with app.app_context():
        db = Database.get_connection('estadio_db_test')

        with db.cursor() as cursor:
            cursor.execute('SELECT DATABASE() AS db')
            actual = cursor.fetchone()['db']
        assert actual == 'estadio_db_test', f'Se esperaba estadio_db_test, se obtuvo {actual}'

        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO patrocinadores
                    (nombre_empresa, rif, tipo_contrato, nombre_contacto,
                     telefono, email, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                ('Empresa Test C.A.', f'J-{uuid.uuid4().hex[:8]}', 1,
                 'Contacto Test', '04120000000', 'test@empresa.com', 1),
            )
            id_patrocinador = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO contrato
                    (id_patrocinador, fecha_inicio, fecha_fin, estado,
                     estatus, tipo, monto_total)
                VALUES (%s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR),
                        %s, %s, %s, %s)
                """,
                (id_patrocinador, '1', 'Vigente', '1', 10000.00),
            )
            id_contrato = cursor.lastrowid
        db.commit()

        modelo = Pago()
        # Asegura que el modelo use siempre la BD de pruebas sin envolver el cursor en MagicMock
        monkeypatch.setattr(modelo, '_get_db', lambda: Database.get_connection('estadio_db_test'))

        referencia = f'REF-{uuid.uuid4().hex[:8]}'
        datos_pago = {
            'id_contrato': id_contrato,
            'monto': 2000.00,
            'tipo_pago': 'Transferencia',
            'referencia': referencia,
            'fecha_pago': '2026-06-01',
            'hora_pago': '12:00:00',
            'registrado_por': 1,
            'descripcion': 'Pago de prueba de integración',
        }

        pago_creado = modelo.registrar_pago(datos_pago)
        assert pago_creado is not None, 'El modelo no pudo registrar el pago'
        assert pago_creado.id_pago is not None, 'El pago no obtuvo id_pago'

        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE pagos SET estado = 1 WHERE id_pago = %s",
                (pago_creado.id_pago,),
            )
            cursor.execute(
                """
                SELECT id_pago, id_contrato, monto, tipo_pago, referencia,
                       estado, registrado_por
                FROM pagos
                WHERE id_pago = %s
                """,
                (pago_creado.id_pago,),
            )
            fila = cursor.fetchone()
        db.commit()

        assert fila is not None, 'El pago no quedó guardado en estadio_db_test'
        assert fila['id_contrato'] == id_contrato
        assert float(fila['monto']) == 2000.00
        assert fila['tipo_pago'] == 'Transferencia'
        assert fila['referencia'] == referencia
        assert fila['estado'] == 1
        assert fila['registrado_por'] == 1

        total_pagado = modelo.get_total_pagado_by_contrato(id_contrato)
        assert total_pagado == 2000.00

        print('\n[BD DE PRUEBA] Pago persistido en estadio_db_test:')
        print(f'  id_patrocinador = {id_patrocinador}')
        print(f'  id_contrato      = {id_contrato}')
        print(f'  id_pago          = {pago_creado.id_pago}')
        print(f'  referencia       = {referencia}')
        print(f'  total_pagado     = {total_pagado}')