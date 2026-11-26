
import pytest


URL_TAREAS = '/gestion-tarea/'


def registrar_tarea(client, nombre='Tarea de prueba',
                    instruccion='Instruccion de prueba valida'):
    """Registra una tarea mediante el controlador."""

    return client.post(URL_TAREAS, data={
        'registrar': '1',
        'Nombre_Tarea': nombre,
        'Instruccion': instruccion
    })


def test_consultar_panel_tareas(client, superadmin):
    """
    Caso: consultar el panel de Gestión de Tareas.
    Resultado esperado: el sistema muestra el panel correctamente.
    """

    respuesta = client.get(URL_TAREAS)

    assert respuesta.status_code == 200
    assert respuesta.content_type.startswith('text/html')


def test_registrar_tarea_correctamente(client, superadmin):
    """
    Caso: registrar una tarea.
    Escenario: el administrador proporciona datos válidos.
    Resultado esperado: la tarea queda registrada.
    """

    respuesta = registrar_tarea(
        client,
        nombre='Prueba funcional registro',
        instruccion='Instruccion valida para registrar'
    )

    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert datos['success'] is True
    assert datos['error'] is None


def test_rechazar_registro_sin_datos(client, superadmin):
    """
    Caso: registrar una tarea sin completar los campos obligatorios.
    Resultado esperado: el sistema rechaza el registro.
    """

    respuesta = client.post(URL_TAREAS, data={
        'registrar': '1',
        'Nombre_Tarea': '',
        'Instruccion': ''
    })

    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert datos['success'] is False
    assert 'obligatorios' in datos['error']


def test_editar_tarea_existente(client, superadmin):
    """
    Caso: editar una tarea existente.
    Resultado esperado: el sistema confirma la modificación.
    """

    registrar_tarea(
        client,
        nombre='Tarea antes de editar',
        instruccion='Instruccion inicial de prueba'
    )

    from app.model.tarea_model import TareaModel

    tarea_model = TareaModel()
    tareas = tarea_model.consultar()

    tarea = next(
        t for t in tareas
        if t['Nombre_Tarea'] == 'Tarea antes de editar'
    )

    respuesta = client.post(URL_TAREAS, data={
        'editar': '1',
        'id_tarea': str(tarea['id_tarea']),
        'Nombre_Tarea': 'Tarea despues de editar',
        'Instruccion': 'Instruccion modificada correctamente'
    })

    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert datos['success'] is True
    assert datos['error'] is None


def test_eliminar_tarea_existente(client, superadmin):
    """
    Caso: eliminar una tarea existente.
    Resultado esperado: la tarea se desactiva mediante eliminación lógica.
    """

    registrar_tarea(
        client,
        nombre='Tarea para eliminar',
        instruccion='Instruccion para prueba de eliminacion'
    )

    from app.model.tarea_model import TareaModel

    tarea_model = TareaModel()
    tareas = tarea_model.consultar()

    tarea = next(
        t for t in tareas
        if t['Nombre_Tarea'] == 'Tarea para eliminar'
    )

    respuesta = client.post(URL_TAREAS, data={
        'eliminar': '1',
        'id_tarea': str(tarea['id_tarea'])
    })

    datos = respuesta.get_json()

    assert respuesta.status_code == 200
    assert datos['success'] is True

    tarea_eliminada = tarea_model.obtener_por_id(tarea['id_tarea'])

    assert tarea_eliminada['Estatus'] == 0
