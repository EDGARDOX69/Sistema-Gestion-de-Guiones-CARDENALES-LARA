"""Aceptación del flujo de tareas asignadas (Mis Tareas).

Se ejecuta con el cliente de Flask sobre ``*_test``, igual que el resto de
pruebas de aceptación. No usa Playwright ni el fixture ``pagina_autenticada``,
que no está definido en este proyecto.
"""
import uuid

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.db]

RUTA = '/gestion-tarea/'


def test_aceptacion_ta_01_acceso_mis_tareas(client, superadmin):
    """Verifica que el usuario autenticado acceda a su vista de tareas asignadas."""
    respuesta = client.get('/gestion-tarea/mis-tareas')
    assert respuesta.status_code == 200

    html = respuesta.get_data(as_text=True)
    assert 'Mis Tareas' in html
    assert 'Tareas asignadas a ti' in html


def test_aceptacion_ta_02_asignar_y_completar_mis_tareas(client, superadmin):
    """Crea, asigna y completa una tarea recorriendo las rutas reales."""
    from app.model.tarea_model import TareaModel, TareasAsignadasModel

    nombre = f'Tarea asignada {uuid.uuid4().hex[:6]}'
    instruccion = 'Instrucción de prueba para la aceptación de mis tareas'
    creada = client.post(RUTA, data={
        'registrar': 'true',
        'Nombre_Tarea': nombre,
        'Instruccion': instruccion,
    })
    assert creada.status_code < 400
    assert creada.get_json()['success'] is True

    consulta = client.post(RUTA, data={'consultar': 'true'})
    assert consulta.status_code < 400
    id_tarea = next(t['id_tarea'] for t in consulta.get_json()
                    if t['Nombre_Tarea'] == nombre)

    asignada = client.post(RUTA, data={
        'asignar': 'true',
        'id_tarea': str(id_tarea),
        'id_usuario': str(superadmin.id),
    })
    assert asignada.status_code < 400
    datos_asignacion = asignada.get_json()
    assert datos_asignacion['success'] is True, datos_asignacion
    assert datos_asignacion['asignados'] == 1

    vista = client.get('/gestion-tarea/mis-tareas')
    assert vista.status_code == 200
    assert nombre in vista.get_data(as_text=True)

    asignaciones = TareasAsignadasModel().consultar(
        id_usuario=superadmin.id, id_tarea=id_tarea
    )
    assert len(asignaciones) == 1
    id_asignacion = asignaciones[0]['id_asignacion']

    completada = client.post(
        '/gestion-tarea/completar',
        data={'id_asignacion': str(id_asignacion)},
        headers={'Accept': 'application/json'},
    )
    assert completada.status_code < 400
    assert completada.get_json()['success'] is True

    assert TareasAsignadasModel().obtener_por_id(id_asignacion)['Estado'] == 'Completada'
    assert TareaModel().obtener_por_id(id_tarea)['Nombre_Tarea'] == nombre
