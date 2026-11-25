"""Fixtures compartidos por toda la suite de pruebas.

Pytest carga este modulo desde el ``conftest.py`` de la raiz. Cualquier test
de ``test/`` o de ``Pruebas por modulo/`` puede pedir estos fixtures.

Regla dura: los tests corren SOLO contra las BDs ``*_test``, clonadas desde
los ``.sql`` de la raiz. Nunca tocan ``estadio_db`` / ``seguridad`` reales.
"""

import uuid

import pytest

from soporte_pruebas import (
    clonar_bases_de_prueba,
    configurar_bd_test,
    parchear_pymysql,
    verificar_conexiones,
)


@pytest.fixture(scope='session')
def bases_de_prueba():
    """Clona los dumps en las BDs de test. Solo se ejecuta si un test la pide.

    No es autouse a proposito: ``pytest -m unit`` debe correr sin MySQL.
    """
    clonar_bases_de_prueba()
    yield


@pytest.fixture()
def app(bases_de_prueba, monkeypatch):
    """Crea la app apuntando a las BDs de prueba y verifica las conexiones."""
    configurar_bd_test(monkeypatch)
    parchear_pymysql(monkeypatch)
    monkeypatch.setenv('SECRET_KEY', 'clave-de-test')

    from app.helpers import email_service
    from app.controller import auth_controller
    monkeypatch.setattr(email_service, 'enviar_email_recuperacion', lambda *a, **k: True)
    monkeypatch.setattr(auth_controller, 'enviar_email_recuperacion', lambda *a, **k: True)

    from app import create_app
    application = create_app()
    application.config['TESTING'] = True
    application.config['WTF_CSRF_ENABLED'] = False
    verificar_conexiones(application)
    yield application


@pytest.fixture(autouse=True)
def _contexto(request):
    """Empuja un app context solo cuando el test toca Flask o la BD."""
    necesita_app = 'app' in request.fixturenames
    necesita_db = request.node.get_closest_marker('db') is not None
    if not (necesita_app or necesita_db):
        yield
        return

    application = request.getfixturevalue('app')
    with application.app_context():
        yield


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app, _contexto):
    """Conexion a estadio_db_test dentro del app context del test."""
    from app.database import Database
    return Database.get_connection('estadio_db')


@pytest.fixture()
def seguridad_db(app, _contexto):
    """Conexion a seguridad_test dentro del app context del test."""
    from app.database import Database
    return Database.get_connection('seguridad')


@pytest.fixture()
def crear_usuario(app):
    """Crea usuarios directamente en seguridad_test."""
    def _crear(rol='Superadmin', activo=True, password='Clave1234'):
        from werkzeug.security import generate_password_hash
        from app.model.auth_model import UsuarioModel
        email = f'test_{uuid.uuid4().hex[:8]}@prueba.com'
        usuario = UsuarioModel().registrar({
            'nombre': 'Usuario Prueba',
            'email': email,
            'password_hash': generate_password_hash(password),
            'cedula': uuid.uuid4().hex[:10],
            'rol': rol,
        })
        assert usuario is not None, 'No se pudo registrar el usuario de prueba'
        if not activo:
            UsuarioModel().modificar(usuario.id, {'activo': 0})
            usuario = UsuarioModel().obtener_por_id(usuario.id)
        usuario._password = password
        return usuario
    return _crear


@pytest.fixture()
def login(client):
    """Login completo; funciona con el CAPTCHA activo o desactivado."""
    def _login(usuario, next_page=None, captcha='ABCD'):
        with client.session_transaction() as s:
            s['captcha_code'] = captcha
        url = '/auth/login'
        if next_page:
            url += f'?next={next_page}'
        return client.post(url, data={
            'email': usuario.email,
            'password': getattr(usuario, '_password', ''),
            'captcha_text': captcha,
        })
    return _login


@pytest.fixture()
def superadmin(client, crear_usuario, login):
    """Cliente con sesion iniciada como Superadmin."""
    usuario = crear_usuario(rol='Superadmin')
    login(usuario)
    return usuario


@pytest.fixture()
def crear_guion(app):
    """Crea un guion (con su fecha de hoy) en estadio_db_test.

    Devuelve el id. Sirve como base para integracion, humo y aceptacion.
    """
    def _crear(nombre='Guion Prueba', estado='borrador', con_fecha=True):
        from app.database import Database
        db = Database.get_connection('estadio_db')
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO guiones (nombre, estado, creado_en, modificado_en, status) "
                "VALUES (%s, %s, NOW(), NOW(), 1)",
                (nombre, estado),
            )
            guion_id = cur.lastrowid
            if con_fecha:
                cur.execute(
                    "INSERT INTO guion_fechas (guion_id, fecha) VALUES (%s, CURDATE())",
                    (guion_id,),
                )
        return guion_id
    return _crear


@pytest.fixture()
def crear_guion_completo(app):
    """Guion + 2 pregame + 2 game en estado ``pendiente``."""
    def _crear(nombre='Guion Completo'):
        from app.database import Database
        db = Database.get_connection('estadio_db')
        with db.cursor() as cur:
            cur.execute("UPDATE guiones SET estado = 'finalizado' WHERE estado = 'en_vivo'")
            cur.execute(
                "INSERT INTO guiones (nombre, estado, creado_en, modificado_en, status) "
                "VALUES (%s, %s, NOW(), NOW(), 1)",
                (nombre, 'publicado'),
            )
            guion_id = cur.lastrowid
            cur.execute(
                "INSERT INTO guion_fechas (guion_id, fecha) VALUES (%s, CURDATE())",
                (guion_id,),
            )
            elementos = [
                ('pregame', None, None, 'Intro musica', 30, 'Keiver', 1),
                ('pregame', None, None, 'Saludo animador', 60, 'Maria', 2),
                ('game', 1, 'alta', 'Promo especial', 120, 'Keiver', 3),
                ('game', 1, 'baja', 'Dinamica publico', 90, 'Maria', 4),
            ]
            for tipo, inning, medio, contenido, dur, encargado, orden in elementos:
                cur.execute(
                    "INSERT INTO elementos_guion (guion_id, tipo, hora, inning, medio_inning, "
                    "contenido, duracion_estimada, encargado, orden, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pendiente')",
                    (guion_id, tipo, '18:30:00', inning, medio, contenido, dur, encargado, orden),
                )
        return guion_id
    return _crear
