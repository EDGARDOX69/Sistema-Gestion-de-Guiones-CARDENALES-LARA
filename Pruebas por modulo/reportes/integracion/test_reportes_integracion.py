"""CP-REP-INT-01: endpoints de reportes y deuda de autorizacion."""

import json

from soporte_api import login_como


def test_dashboard_y_campos_para_superadmin(superadmin, client):
    respuesta = client.get('/reportes/')
    assert respuesta.status_code == 200

    respuesta = client.get('/reportes/campos/guiones')
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_json()
    assert isinstance(cuerpo['campos'], dict)
    assert 'nombre' in cuerpo['campos']


def test_preview_devuelve_estructura_estable(superadmin, client):
    respuesta = client.post('/reportes/preview', data={'modulo': 'guiones'})
    assert respuesta.status_code == 200

    data = json.loads(respuesta.data)
    assert {'datos', 'total', 'kpis', 'modulo'} <= set(data)
    assert data['total'] == len(data['datos'])

    respuesta = client.post('/reportes/preview', data={'modulo': 'no_existe'})
    assert respuesta.status_code == 400


def test_descargar_inexistente_devuelve_404(superadmin, client):
    respuesta = client.get('/reportes/descargar/no-existe.pdf')
    assert respuesta.status_code == 404


def test_campos_exige_permiso_de_reportes(app, crear_usuario):
    usuario = crear_usuario(rol='Usuario')
    cliente = login_como(app, usuario)

    respuesta = cliente.get('/reportes/campos/guiones')
    assert respuesta.status_code == 302
    assert '/dashboard' in respuesta.headers['Location']


def test_reporte_administrador_con_permiso_accede(app, crear_usuario):
    usuario = crear_usuario(rol='Administrador')
    cliente = login_como(app, usuario)

    assert cliente.get('/reportes/').status_code == 200
    assert cliente.get('/reportes/campos/guiones').status_code == 200


def test_preview_sin_permiso_devuelve_403(app, crear_usuario):
    usuario = crear_usuario(rol='Usuario')
    cliente = login_como(app, usuario)

    respuesta = cliente.post('/reportes/preview', data={'modulo': 'guiones'})
    assert respuesta.status_code == 403
