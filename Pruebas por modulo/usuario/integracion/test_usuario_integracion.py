"""CP-USU-INT-01: CRUD y contrasena del modulo Usuarios."""

import uuid

from werkzeug.security import check_password_hash

from app.model.usuario_model import UsuarioModel


def _datos_usuario(sufijo):
    return {
        'nombre': f'Usuario {sufijo}',
        'email': f'usuario_{sufijo}@prueba.com',
        'cedula': f'V{sufijo[:8]}',
        'rol': 'Usuario',
        'departamento': 'Medios',
        'telefono': '04120000000',
        'password': 'Clave1234',
        'activo': '1',
    }


def test_registrar_y_editar_sin_password_conserva_hash(superadmin, client, seguridad_db):
    sufijo = uuid.uuid4().hex[:8]
    datos = _datos_usuario(sufijo)

    respuesta = client.post('/usuarios/', data={'registrar': '1', **datos})
    assert respuesta.status_code == 200
    assert 'registrado' in respuesta.get_json()['mensaje'].lower()

    with seguridad_db.cursor() as cur:
        cur.execute('SELECT * FROM usuarios WHERE email = %s', (datos['email'],))
        usuario = cur.fetchone()
    assert usuario is not None
    hash_original = usuario['password_hash']

    respuesta = client.post('/usuarios/', data={
        'editar': usuario['id'],
        'nombre': datos['nombre'],
        'email': datos['email'],
        'cedula': datos['cedula'],
        'rol': datos['rol'],
        'departamento': datos['departamento'],
        'telefono': '04120000001',
        'activo': '1',
    })
    assert respuesta.status_code == 200
    assert 'actualizado' in respuesta.get_json()['mensaje'].lower()

    with seguridad_db.cursor() as cur:
        cur.execute('SELECT password_hash FROM usuarios WHERE id = %s', (usuario['id'],))
        assert cur.fetchone()['password_hash'] == hash_original


def test_no_permite_eliminar_el_propio_usuario(superadmin, client, seguridad_db):
    respuesta = client.post('/usuarios/', data={'eliminar': superadmin.id})

    assert respuesta.status_code == 200
    assert 'propio usuario' in respuesta.get_json()['mensaje'].lower()

    with seguridad_db.cursor() as cur:
        cur.execute('SELECT id FROM usuarios WHERE id = %s', (superadmin.id,))
        assert cur.fetchone() is not None


def test_cambiar_contrasena_actualiza_hash(crear_usuario, login, client, seguridad_db):
    usuario = crear_usuario(rol='Usuario')
    login(usuario)

    respuesta = client.post('/usuarios/cambiar-contrasena', data={
        'password_actual': 'Clave1234',
        'password_nueva': 'NuevaClave123',
        'confirmar_password': 'NuevaClave123',
    })
    assert respuesta.status_code == 302
    assert '/auth/login' in respuesta.headers['Location']

    with seguridad_db.cursor() as cur:
        cur.execute('SELECT password_hash FROM usuarios WHERE id = %s', (usuario.id,))
        nuevo_hash = cur.fetchone()['password_hash']
    assert check_password_hash(nuevo_hash, 'NuevaClave123')
    assert not check_password_hash(nuevo_hash, 'Clave1234')


def test_modelo_rechaza_rol_invalido():
    modelo = UsuarioModel()
    try:
        modelo.set_rol('Root')
    except ValueError:
        return
    raise AssertionError('El modelo acepto un rol fuera del catalogo')
