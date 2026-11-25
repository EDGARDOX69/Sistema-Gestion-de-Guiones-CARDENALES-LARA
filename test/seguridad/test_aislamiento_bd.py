"""Pruebas del aislamiento de la suite respecto a las bases reales.

Cada prueba de este archivo intenta llegar a ``estadio_db`` o ``seguridad``
por una via distinta. Si alguna redireccion falla, el test debe fallar antes
de que la suite pueda escribir en produccion.
"""

import pymysql
import pytest

from soporte_pruebas import credenciales


pytestmark = pytest.mark.db


def _nombre_unico(prefijo):
    from uuid import uuid4
    return f'{prefijo}-{uuid4().hex[:10]}'


def test_conexiones_logicas_apuntan_a_bases_de_prueba(app):
    """CP-AIS-INT-01: las conexiones de la app usan los esquemas *_test."""
    from app.database import Database

    with app.app_context():
        for nombre, esperado in (
            ('estadio_db', 'estadio_db_test'),
            ('seguridad', 'seguridad_test'),
            ('estadio_db_test', 'estadio_db_test'),
            ('seguridad_test', 'seguridad_test'),
        ):
            with Database.get_connection(nombre).cursor() as cur:
                cur.execute('SELECT DATABASE() AS db')
                assert cur.fetchone()['db'] == esperado, nombre


def test_consulta_explicita_a_seguridad_se_redirige(db, crear_usuario):
    """CP-AIS-INT-02: un JOIN con ``seguridad.`` lee seguridad_test."""
    usuario = crear_usuario()

    with db.cursor() as cur:
        cur.execute(
            'SELECT COUNT(*) AS total FROM seguridad.usuarios WHERE email = %s',
            (usuario.email,),
        )
        assert cur.fetchone()['total'] == 1


def test_consulta_explicita_a_estadio_se_redirige(seguridad_db, crear_guion):
    """CP-AIS-INT-03: un FROM con ``estadio_db.`` lee estadio_db_test."""
    guion_id = crear_guion(nombre=_nombre_unico('Aislamiento'))

    with seguridad_db.cursor() as cur:
        cur.execute(
            'SELECT COUNT(*) AS total FROM estadio_db.guiones WHERE id = %s',
            (guion_id,),
        )
        assert cur.fetchone()['total'] == 1


def test_conexion_directa_con_nombre_real_se_redirige(app):
    """CP-AIS-INT-04: pymysql.connect(database='estadio_db') no toca la real."""
    with app.app_context():
        conn = pymysql.connect(database='estadio_db', **credenciales())
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT DATABASE() AS db')
                assert cur.fetchone()[0] == 'estadio_db_test'
        finally:
            conn.close()
