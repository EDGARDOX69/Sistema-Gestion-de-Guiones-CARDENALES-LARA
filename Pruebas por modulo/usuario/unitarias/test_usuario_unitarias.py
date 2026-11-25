from app.model.usuario_model import UsuarioModel


def _modelo():
    modelo = UsuarioModel()
    modelo.set_nombre('Usuario Prueba')
    modelo.set_email('usuario@prueba.com')
    modelo.set_cedula('12345678')
    modelo.set_rol('Usuario')
    return modelo


def test_usuario_valido():
    assert _modelo()._validar_datos_usuario() is True


def test_usuario_con_email_invalido():
    modelo = _modelo()
    modelo.set_email('correo-invalido')
    assert modelo._validar_datos_usuario() is False
