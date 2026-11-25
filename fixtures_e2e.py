"""Servidor y usuario para las pruebas end-to-end con Playwright.

El servidor se levanta en un puerto propio y siempre contra
``estadio_db_test`` y ``seguridad_test``. Nunca se reutiliza un servidor que
ya este escuchando, porque podria apuntar a las bases reales.

Se activa explicitamente::

    E2E=1 pytest test/interfaz
    E2E=1 pytest "Pruebas por modulo"
"""

import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest

from soporte_pruebas import (
    clonar_bases_de_prueba,
    crear_usuario_e2e as _insertar_usuario_e2e,
    env_bd_test,
)


RAIZ = Path(__file__).resolve().parent
PYTHON = os.environ.get('E2E_PYTHON', sys.executable)
PUERTO = int(os.environ.get('E2E_PORT', '5002'))
BASE_URL = f'http://127.0.0.1:{PUERTO}'
LOGIN = f'{BASE_URL}/auth/login'

COMANDO = [
    PYTHON,
    '-c',
    (
        'from app import create_app, socketio; '
        'socketio.run(create_app(), host="127.0.0.1", '
        f'port={PUERTO}, debug=False, use_reloader=False, '
        'allow_unsafe_werkzeug=True)'
    ),
]


def _responde(url, timeout=1.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout):
            return True
    except Exception:
        return False


def _esperar(url, proceso, limite=120.0):
    inicio = time.time()
    while time.time() - inicio < limite:
        if _responde(url):
            return
        if proceso.poll() is not None:
            raise RuntimeError(
                f'El servidor E2E termino antes de responder. '
                f'Revisa el log: {proceso.log.name}'
            )
        time.sleep(0.5)
    raise RuntimeError(f'El servidor E2E no respondio en {limite:.0f} s: {url}')


@pytest.fixture(scope='session')
def servidor():
    if os.getenv('E2E') != '1':
        raise RuntimeError(
            'Las pruebas de interfaz requieren E2E=1. '
            'No se marcan como skipped: deben excluirse en la recoleccion.'
        )

    if _responde(LOGIN):
        raise RuntimeError(
            f'El puerto {PUERTO} ya esta ocupado por otro servidor. '
            'Detenlo o usa E2E_PORT para elegir otro puerto. '
            'No se reutiliza para no arriesgar las bases reales.'
        )

    clonar_bases_de_prueba()
    credenciales = _insertar_usuario_e2e()
    log = tempfile.NamedTemporaryFile(
        prefix='itinerario_e2e_', suffix='.log', delete=False,
    )
    proceso = subprocess.Popen(
        COMANDO,
        cwd=RAIZ,
        env=env_bd_test(),
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        _esperar(LOGIN, proceso)
        yield {'url': BASE_URL, 'credenciales': credenciales}
    finally:
        proceso.terminate()
        try:
            proceso.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proceso.kill()
            proceso.wait(timeout=5)
        log.close()


@pytest.fixture(scope='session')
def base_url(servidor):
    return servidor['url']


@pytest.fixture(scope='session')
def e2e_credenciales(servidor):
    return servidor['credenciales']


@pytest.fixture()
def crear_usuario_e2e():
    """Crea actores adicionales en ``seguridad_test`` para flujos multi-usuario.

    Devuelve un objeto con ``id``, ``nombre``, ``email`` y ``password`` para que
    las pruebas puedan autenticar cada contexto con credenciales propias.
    """
    def _crear(rol='Administrador', nombre=None, password='Clave1234'):
        datos = _insertar_usuario_e2e(
            rol=rol,
            password=password,
            nombre=nombre or f'Usuario E2E {uuid.uuid4().hex[:5]}',
        )
        return SimpleNamespace(**datos)
    return _crear


@pytest.fixture()
def autenticar_contexto(servidor):
    """Inicia sesión en un contexto de Playwright con login real.

    Depende de ``servidor`` (no de ``base_url``) para garantizar que el servidor
    E2E esté levantado: pytest-playwright define su propio fixture ``base_url``.
    Lee el CAPTCHA del DOM solo si está activo; no inyecta cookies. Cierra la
    página intermedia, dejando la sesión en el contexto para las páginas que
    creen los tests.
    """
    url = servidor['url']

    def _autenticar(contexto, usuario):
        from playwright.sync_api import expect

        pagina = contexto.new_page()
        pagina.goto(f'{url}/auth/login')
        if pagina.locator('#captcha_text').count():
            tiles = pagina.locator('.captcha-tile')
            expect(tiles).to_have_count(4)
            codigo = ''.join(texto.strip() for texto in tiles.all_text_contents())
            pagina.fill('#captcha_text', codigo)
        pagina.fill('#email', usuario.email)
        pagina.fill('#password', getattr(usuario, 'password', 'Clave1234'))
        pagina.click('#btnLogin')
        pagina.wait_for_url(re.compile(r'/dashboard'), timeout=30_000)
        pagina.close()
    return _autenticar
