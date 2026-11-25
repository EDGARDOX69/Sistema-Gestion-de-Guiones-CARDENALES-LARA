import re
import uuid

from playwright.sync_api import expect

from soporte_modulos import RUTA_INTERFAZ
from soporte_ui import login


def test_gestion_tarea_interfaz_carga(page, e2e_credenciales):
    login(page, e2e_credenciales)
    respuesta = page.goto(RUTA_INTERFAZ['gestion_tarea'])
    assert respuesta.status == 200
    expect(page.get_by_role('heading', name='Gestión de Tareas')).to_be_visible()
    expect(page.locator('#tablaTareas')).to_be_visible()
    expect(page.get_by_role('button', name=re.compile('Nueva Tarea'))).to_be_visible()
    expect(page.get_by_role('button', name=re.compile('Asignar Tarea'))).to_be_visible()


def _crear_tarea(page):
    nombre = f'Tarea UI {uuid.uuid4().hex[:8]}'
    page.get_by_role('button', name=re.compile('Nueva Tarea')).click()
    page.locator('#formCrearTarea [name="Nombre_Tarea"]').fill(nombre)
    page.locator('#formCrearTarea [name="Instruccion"]').fill(
        'Instrucciones creadas desde la prueba Playwright'
    )
    page.locator('#formCrearTarea button[type="submit"]').click()
    page.get_by_role('button', name='Sí, crear').click()
    fila = page.locator('#tablaTareas tbody tr').filter(has_text=nombre)
    expect(fila).to_be_visible(timeout=15_000)
    return nombre, fila


def test_gestion_tarea_crear_y_editar_desde_la_interfaz(page, e2e_credenciales):
    login(page, e2e_credenciales)
    page.goto(RUTA_INTERFAZ['gestion_tarea'])

    nombre, fila = _crear_tarea(page)
    id_tarea = fila.locator('td').first.inner_text()
    nombre_editado = f'{nombre} editada'

    fila.get_by_role('button', name='Editar').click()
    page.locator('#edit_Nombre_Tarea').fill(nombre_editado)
    page.locator('#edit_Instruccion').fill(
        'Instrucciones actualizadas desde Playwright'
    )
    page.locator('#formEditarTarea button[type="submit"]').click()
    page.get_by_role('button', name='Sí, guardar').click()

    fila_editada = page.locator('#tablaTareas tbody tr').filter(
        has_text=nombre_editado
    )
    expect(fila_editada).to_be_visible(timeout=15_000)
    expect(fila_editada.locator('td').first).to_have_text(id_tarea)


def test_gestion_tarea_asignar_y_completar_desde_mis_tareas(
    page, e2e_credenciales
):
    login(page, e2e_credenciales)
    page.goto(RUTA_INTERFAZ['gestion_tarea'])

    nombre, fila = _crear_tarea(page)
    id_tarea = fila.locator('td').first.inner_text()

    page.get_by_role('button', name=re.compile('Asignar Tarea')).click()
    page.locator('#modalAsignarTarea select[name="id_tarea"]').select_option(
        value=id_tarea
    )
    page.locator('#asig_usuarios').select_option(
        value=str(e2e_credenciales['id'])
    )
    page.locator('#formAsignarTarea button[type="submit"]').click()
    page.get_by_role('button', name='Sí, asignar').click()
    expect(page.get_by_role('heading', name='Operación exitosa')).to_be_visible()

    page.goto('/gestion-tarea/mis-tareas')
    tarjeta = page.locator('.bento-card').filter(has_text=nombre)
    expect(tarjeta).to_be_visible()
    tarjeta.get_by_role('button', name='Completar').click()

    expect(tarjeta.get_by_text('Finalizada')).to_be_visible(timeout=15_000)
