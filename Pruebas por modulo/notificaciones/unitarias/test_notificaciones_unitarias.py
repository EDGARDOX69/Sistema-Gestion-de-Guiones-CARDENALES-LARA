from app.model.notificacion_model import TIPOS_VALIDOS, NotificacionModel


def test_tipos_validos():
    assert 'tarea_asignada' in TIPOS_VALIDOS
    assert 'tarea_completada' in TIPOS_VALIDOS


def test_tipo_invalido_no_escribe():
    assert NotificacionModel().crear(1, 'otro', 'Titulo', 'Mensaje') is None
