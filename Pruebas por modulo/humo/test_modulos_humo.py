"""CP-GEN-HUM-01: humo de las paginas principales de todos los modulos."""

import pytest

pytestmark = pytest.mark.smoke


RUTAS = {
    'dashboard': '/dashboard',
    'guion': '/guiones/',
    'en_vivo': '/en-vivo/',
    'balance': '/balance/',
    'contratos': '/contratos/',
    'patrocinadores': '/patrocinador/',
    'premios': '/premio/',
    'inventario': '/inventario/',
    'mantenimiento': '/mantenimiento/',
    'tareas': '/gestion-tarea/',
    'reels': '/reels/',
    'usuarios': '/usuarios/',
    'roles': '/roles/',
    'reportes': '/reportes/',
    'bitacora': '/bitacora/',
    'asistente': '/asistente/',
}


@pytest.mark.parametrize('modulo,ruta', RUTAS.items())
def test_pagina_principal_responde_con_superadmin(modulo, ruta, superadmin, client):
    respuesta = client.get(ruta)
    assert respuesta.status_code == 200, f'{modulo}: {respuesta.status_code}'


@pytest.mark.parametrize('modulo,ruta', RUTAS.items())
def test_pagina_principal_sin_sesion_no_devuelve_200(modulo, ruta, client):
    respuesta = client.get(ruta)
    esperados = {401} if modulo in {'dashboard', 'asistente'} else {302}
    assert respuesta.status_code in esperados, f'{modulo}: {respuesta.status_code}'


@pytest.mark.parametrize('ruta', [
    '/roles/',
    '/bitacora/',
    '/gestion-tarea/',
    '/inventario/gestion-asignaciones',
])
def test_rutas_administrativas_rechazan_rol_basico(ruta, crear_usuario, login, client):
    usuario = crear_usuario(rol='Usuario')
    login(usuario)

    respuesta = client.get(ruta)
    assert respuesta.status_code == 302
