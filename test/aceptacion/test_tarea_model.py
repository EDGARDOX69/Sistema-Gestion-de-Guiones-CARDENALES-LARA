"""Aceptación del catálogo de tareas con el cliente de Flask.

Las pruebas de ``test/aceptacion`` ejercitan rutas reales contra ``*_test``
usando ``client`` y ``superadmin``. El fixture ``pagina_autenticada`` no existe
en el proyecto: las pruebas de navegador viven en
``Pruebas por modulo/<modulo>/interface`` y requieren ``E2E=1``.
"""
import uuid

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.db]

RUTA = '/gestion-tarea/'


def _crear_tarea(client, superadmin):
    """Crea una tarea por la ruta real y devuelve su nombre único."""
    nombre = f'Tarea aceptación {uuid.uuid4().hex[:6]}'
    respuesta = client.post(RUTA, data={
        'registrar': 'true',
        'Nombre_Tarea': nombre,
        'Instruccion': 'Instrucción de prueba para la aceptación del catálogo',
    })
    assert respuesta.status_code < 400
    datos = respuesta.get_json()
    assert datos['success'] is True, datos
    return nombre


def test_aceptacion_gt_01_acceso_dashboard_tareas(client, superadmin):
    """Verifica acceso al dashboard de gestión de tareas y presencia de la tabla."""
    respuesta = client.get(RUTA)
    assert respuesta.status_code == 200

    html = respuesta.get_data(as_text=True)
    assert 'Gestión de Tareas' in html
    assert 'id="tablaTareas"' in html


def test_aceptacion_gt_02_consulta_catalogo_sin_errores(client, superadmin):
    """Una tarea creada desde la ruta real aparece en la consulta del catálogo."""
    nombre = _crear_tarea(client, superadmin)

    respuesta = client.post(RUTA, data={'consultar': 'true'})
    assert respuesta.status_code < 400

    tareas = respuesta.get_json()
    assert isinstance(tareas, list)
    assert any(t['Nombre_Tarea'] == nombre for t in tareas), tareas
