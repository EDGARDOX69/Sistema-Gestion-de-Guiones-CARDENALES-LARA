"""CP-BAL-HUM-01: humo del modulo Balance."""

import uuid

from app.model.balance_model import Pago
from app.database import Database


def test_conexion_a_la_bd_de_prueba(app):
    with app.app_context():
        db = Database.get_connection('estadio_db_test')
        with db.cursor() as cur:
            cur.execute('SELECT 1 AS ok')
            assert cur.fetchone()['ok'] == 1

        assert isinstance(Pago().obtener_contratos_activos(), list)


def test_rutas_principales_no_devuelven_500(superadmin, client, db):
    sufijo = uuid.uuid4().hex[:8]
    with db.cursor() as cur:
        cur.execute(
            'INSERT INTO patrocinadores (nombre_empresa) VALUES (%s)',
            (f'Sponsor Humo {sufijo}',),
        )
        id_patrocinador = cur.lastrowid
        cur.execute(
            'INSERT INTO contrato (id_patrocinador, monto_total, estado) '
            'VALUES (%s, 1000.00, 1)',
            (id_patrocinador,),
        )
        id_contrato = cur.lastrowid

    for ruta in (
        '/balance/',
        f'/balance/api/contrato/{id_contrato}',
        f'/balance/contrato/{id_contrato}/pdf',
    ):
        respuesta = client.get(ruta)
        assert respuesta.status_code == 200, ruta


def test_registro_vacio_redirige_sin_500(superadmin, client):
    respuesta = client.post('/balance/registrar-pago', data={})
    assert respuesta.status_code == 302
