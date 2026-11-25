from werkzeug.security import generate_password_hash
from app.model.auth_model import Usuario


def test_superadmin_tiene_permiso():
    assert Usuario(rol='Superadmin').tiene_permiso('reportes.view')


def test_password_hash_y_verificacion():
    usuario = Usuario()
    usuario.password_hash = generate_password_hash('Clave1234')
    assert usuario.check_password('Clave1234')
    assert not usuario.check_password('incorrecta')
