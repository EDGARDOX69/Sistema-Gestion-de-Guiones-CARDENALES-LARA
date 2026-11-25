"""Soporte compartido para las pruebas de Itinerario.

Concentra la clonacion de las bases ``*_test`` y el blindaje contra las
bases reales. Lo usan ``test/conftest.py`` y ``Pruebas por modulo/conftest.py``
para que ambos conjuntos apliquen exactamente la misma regla.
"""

import os
import re
import uuid
from pathlib import Path

import pymysql
from pymysql.constants import CLIENT
from pymysql.cursors import DictCursor

ROOT = Path(__file__).resolve().parent

TEST_DBS = {'estadio_db': 'estadio_db_test', 'seguridad': 'seguridad_test'}

_RE_ESQUEMA = re.compile(r'(?<![A-Za-z0-9_`])(?:`)?(estadio_db|seguridad)(?:`)?\.')
_RE_DUMP = re.compile(r'`(estadio_db|seguridad)`')


def credenciales():
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'charset': 'utf8mb4',
    }


def redirigir_esquemas(sql):
    """Reescribe las referencias explicitas a los esquemas reales.

    Algunos modelos escriben ``JOIN seguridad.usuarios`` o ``FROM
    estadio_db.pagos``. Esas consultas no pasan por la configuracion de
    conexion, asi que se corrigen en el cursor de prueba.
    """
    if not sql or not isinstance(sql, str):
        return sql
    return _RE_ESQUEMA.sub(lambda m: f'{m.group(1)}_test.', sql)


class DictCursorTest(DictCursor):
    """Cursor que redirige cualquier referencia a los esquemas reales."""

    def execute(self, query, args=None):
        return super().execute(redirigir_esquemas(query), args)

    def executemany(self, query, args):
        return super().executemany(redirigir_esquemas(query), args)


def ruta_dump(archivo):
    ruta = ROOT / archivo
    if not ruta.exists() or ruta.stat().st_size < 100:
        raise FileNotFoundError(
            f'No se encontro el dump {ruta}. '
            'Los tests necesitan estadio_db.sql y seguridad.sql en la raiz.'
        )
    return ruta


def aplicar_dump(conn, archivo):
    """Aplica un dump renombrando solo los esquemas entre backticks."""
    sql = ruta_dump(archivo).read_text(encoding='utf-8')
    sql = _RE_DUMP.sub(lambda m: f'`{m.group(1)}_test`', sql)
    with conn.cursor() as cur:
        cur.execute(sql)
        while cur.nextset():
            pass


def clonar_bases_de_prueba():
    """Elimina y recrea estadio_db_test y seguridad_test desde los dumps."""
    from dotenv import load_dotenv

    load_dotenv(ROOT / '.env')
    conn = pymysql.connect(client_flag=CLIENT.MULTI_STATEMENTS, **credenciales())
    try:
        with conn.cursor() as cur:
            for test in TEST_DBS.values():
                cur.execute(f'DROP DATABASE IF EXISTS `{test}`')
                cur.execute(f'CREATE DATABASE `{test}` DEFAULT CHARACTER SET utf8mb4')
        aplicar_dump(conn, 'estadio_db.sql')
        aplicar_dump(conn, 'seguridad.sql')
    finally:
        conn.close()


def configurar_bd_test(monkeypatch):
    """Apunta la configuracion de la app a las bases de prueba.

    Usa ``monkeypatch.setitem`` para que la configuracion real se restaure al
    terminar el test. Tambien crea los alias ``estadio_db_test`` y
    ``seguridad_test`` que usan algunos tests de modulo.
    """
    from app import config

    for origen, test in TEST_DBS.items():
        base = config.DATABASE_CONFIG[origen]
        monkeypatch.setitem(base, 'database', test)
        monkeypatch.setitem(
            config.DATABASE_CONFIG,
            test,
            {**base, 'database': test},
        )

    import app.database as database

    monkeypatch.setattr(database, 'DictCursor', DictCursorTest)


def parchear_pymysql(monkeypatch):
    """Redirige cualquier conexion directa que pida un esquema real."""
    original = pymysql.connect

    def connect_seguro(*args, **kwargs):
        db = kwargs.get('database')
        if db in TEST_DBS:
            kwargs['database'] = TEST_DBS[db]
        if len(args) >= 4 and args[3] in TEST_DBS:
            args = list(args)
            args[3] = TEST_DBS[args[3]]
        return original(*args, **kwargs)

    monkeypatch.setattr(pymysql, 'connect', connect_seguro)


def verificar_conexiones(application):
    """Falla si alguna conexion de la app no apunta a su base de prueba."""
    from app.database import Database

    esperados = {**TEST_DBS, **{test: test for test in TEST_DBS.values()}}
    with application.app_context():
        for nombre, esperado in esperados.items():
            with Database.get_connection(nombre).cursor() as cur:
                cur.execute('SELECT DATABASE() AS db')
                actual = cur.fetchone()['db']
            if actual != esperado:
                raise AssertionError(
                    f'La conexion {nombre!r} apunta a {actual!r}; '
                    f'se esperaba {esperado!r}.'
                )


def crear_usuario_e2e(rol='Superadmin', password='Clave1234', email=None,
                      nombre='Usuario E2E'):
    """Crea un usuario real dentro de seguridad_test para Playwright."""
    from werkzeug.security import generate_password_hash

    email = email or f'e2e_{uuid.uuid4().hex[:8]}@prueba.com'
    cedula = f'E2E{uuid.uuid4().hex[:8]}'
    conn = pymysql.connect(
        database=TEST_DBS['seguridad'],
        autocommit=True,
        **credenciales(),
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios "
                "(nombre, email, password_hash, cedula, rol, departamento, "
                " activo, fecha_registro) "
                "VALUES (%s, %s, %s, %s, %s, %s, 1, NOW())",
                (
                    nombre,
                    email,
                    generate_password_hash(password),
                    cedula,
                    rol,
                    'Palco de Operaciones',
                ),
            )
            usuario_id = cur.lastrowid
    finally:
        conn.close()
    return {'id': usuario_id, 'nombre': nombre, 'email': email, 'password': password}


def env_bd_test(extra=None):
    """Variables de entorno para el subproceso del servidor E2E."""
    env = os.environ.copy()
    env.update({
        'DB_NAME_ESTADIO': TEST_DBS['estadio_db'],
        'DB_NAME_SEGURIDAD': TEST_DBS['seguridad'],
        'SECRET_KEY': 'clave-e2e',
        'PYTHONIOENCODING': 'utf-8',
    })
    if extra:
        env.update(extra)
    return env
