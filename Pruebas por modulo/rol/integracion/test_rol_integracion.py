"""CP-ROL-INT-01: creacion y edicion de roles con sus permisos."""

import uuid

from app.model.rol_model import RolModel


def test_crear_y_editar_rol_con_permisos(superadmin, client, seguridad_db):
    with seguridad_db.cursor() as cur:
        cur.execute('SELECT id FROM permisos ORDER BY id LIMIT 3')
        permisos = [fila['id'] for fila in cur.fetchall()]
    assert len(permisos) >= 3

    nombre = f'RolPrueba{uuid.uuid4().hex[:8]}'
    respuesta = client.post('/roles/crear', data={
        'nombre': nombre,
        'permisos': [str(permisos[0]), str(permisos[1])],
    })
    assert respuesta.status_code == 302

    with seguridad_db.cursor() as cur:
        cur.execute('SELECT id FROM roles WHERE nombre = %s', (nombre,))
        rol = cur.fetchone()
    assert rol is not None

    respuesta = client.get(f'/roles/editar-rol/{rol["id"]}')
    assert respuesta.status_code == 200

    respuesta = client.post(f'/roles/editar-rol/{rol["id"]}', data={
        'permisos': [str(permisos[1]), str(permisos[2])],
    })
    assert respuesta.status_code == 302

    with seguridad_db.cursor() as cur:
        cur.execute(
            'SELECT permiso_id FROM rol_permiso WHERE rol_id = %s ORDER BY permiso_id',
            (rol['id'],),
        )
        actuales = {fila['permiso_id'] for fila in cur.fetchall()}
    assert actuales == {permisos[1], permisos[2]}

    assert RolModel().obtener_por_nombre(nombre)['id'] == rol['id']


def test_listar_usuarios_y_rol_inexistente(superadmin, client):
    respuesta = client.post('/roles/', data={'listar_usuarios': '1'})
    assert respuesta.status_code == 200
    assert isinstance(respuesta.get_json(), list)

    respuesta = client.get('/roles/editar-rol/999999')
    assert respuesta.status_code == 404
