"""CP-BIT-INT-01: dashboard y reporte por usuario de la bitacora."""

from app.model.bitacora_model import ActividadModel


def test_dashboard_y_reporte_por_usuario(superadmin, client):
    respuesta = client.get('/bitacora/')
    assert respuesta.status_code == 200

    actividades = ActividadModel().consultar(usuario_id=superadmin.id)
    assert actividades, 'El login del fixture debe registrar una actividad'

    respuesta = client.get(f'/bitacora/usuario/{superadmin.id}')
    assert respuesta.status_code == 200
    texto = respuesta.get_data(as_text=True).lower()
    assert 'inicio de sesi' in texto or 'auth' in texto

    respuesta = client.get(
        f'/bitacora/usuario/{superadmin.id}?modulo=auth&tipo_accion=login'
    )
    assert respuesta.status_code == 200
    assert 'auth' in respuesta.get_data(as_text=True).lower()


def test_usuario_inexistente_redirige_al_dashboard(superadmin, client):
    respuesta = client.get('/bitacora/usuario/999999')
    assert respuesta.status_code == 302
    assert '/bitacora/' in respuesta.headers['Location']
