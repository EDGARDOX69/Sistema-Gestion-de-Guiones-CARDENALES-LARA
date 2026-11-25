"""TA-UI — Flujo end-to-end de Tareas y Notificaciones con Playwright.

Adaptacion de la prueba que estaba escrita contra fixtures inexistentes
(``servidor_live``) y contra el rol ``Empleado`` (no sembrado en la BD).
Ahora usa los fixtures reales del proyecto, igual que
``test/interfaz/test_tareas_asignadas.py``:

* ``servidor`` / ``browser``: servidor propio en ``estadio_db_test``.
* ``autenticar_contexto``: login real (CAPTCHA solo si la app lo activa).
* ``crear_usuario_e2e``: actores reales en ``seguridad_test``.

Ejecucion::

    $env:E2E='1'
    .\\.venv\\Scripts\\python.exe -m pytest test/interfaz/test_tarea_model_interfaz.py -q
"""
import re
import uuid

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.ui


def test_flujo_completo_tareas_notificaciones_y_seguimiento(
    browser, servidor, autenticar_contexto, crear_usuario_e2e
):
    """Crear, editar, asignar, completar, notificar, supervisar y eliminar."""
    url = servidor['url']
    supervisor = crear_usuario_e2e(rol='Administrador', nombre='Supervisor UI')
    empleado = crear_usuario_e2e(rol='Usuario', nombre='Empleado UI')

    ctx_admin = browser.new_context()
    ctx_emp = browser.new_context()
    autenticar_contexto(ctx_admin, supervisor)
    autenticar_contexto(ctx_emp, empleado)
    page_admin = ctx_admin.new_page()
    page_emp = ctx_emp.new_page()

    sufijo = uuid.uuid4().hex[:6]
    nombre_original = f'Tarea UI {sufijo}'
    nombre_editado = f'{nombre_original} editada'
    instruccion = f'Instruccion de prueba {sufijo}'

    try:
        # 1. Panel de gestión de tareas.
        page_admin.goto(f'{url}/gestion-tarea/')
        tabla = page_admin.locator('#tablaTareas')
        expect(tabla).to_be_visible()
        expect(page_admin.locator('[data-bs-target="#modalCrearTarea"]')).to_be_visible()

        # 2. Alta: validación vacía y creación confirmada.
        page_admin.locator('[data-bs-target="#modalCrearTarea"]').click()
        modal_crear = page_admin.locator('#modalCrearTarea')
        expect(modal_crear).to_be_visible()

        modal_crear.locator('button[type="submit"]').click()
        expect(page_admin.locator('.swal2-popup')).to_contain_text('Error de validación')
        page_admin.locator('.swal2-confirm').click()

        modal_crear.locator('input[name="Nombre_Tarea"]').fill(nombre_original)
        modal_crear.locator('textarea[name="Instruccion"]').fill(instruccion)
        modal_crear.locator('button[type="submit"]').click()
        page_admin.get_by_role('button', name=re.compile(r'S[ií], crear', re.I)).click()
        expect(page_admin.locator('.swal2-popup')).to_contain_text('Operación exitosa')
        expect(tabla.locator('tbody tr', has_text=nombre_original)).to_have_count(1, timeout=15_000)

        # 3. Edición desde la fila de la tabla.
        fila = tabla.locator('tbody tr', has_text=nombre_original).first
        fila.locator('button[title="Editar"]').click()
        modal_editar = page_admin.locator('#modalEditarTarea')
        expect(modal_editar).to_be_visible()

        modal_editar.locator('#edit_Nombre_Tarea').fill(nombre_editado)
        modal_editar.locator('#edit_Instruccion').fill(f'{instruccion} (editada)')
        modal_editar.locator('button[type="submit"]').click()
        page_admin.get_by_role('button', name=re.compile(r'S[ií], guardar', re.I)).click()
        expect(page_admin.locator('.swal2-popup')).to_contain_text('Operación exitosa')
        expect(tabla.locator('tbody tr', has_text=nombre_editado)).to_have_count(1, timeout=15_000)

        # 4. Asignación: validar sin destinatario y luego asignar al empleado.
        page_admin.locator('[data-bs-target="#modalAsignarTarea"]').click()
        modal_asignar = page_admin.locator('#modalAsignarTarea')
        expect(modal_asignar).to_be_visible()

        # Se elige la tarea primero: el <select> es required y, si está vacío,
        # la validación nativa impide llegar al mensaje propio de la app.
        select_tarea = modal_asignar.locator('select[name="id_tarea"]')
        opcion_valor = (
            select_tarea.locator('option', has_text=nombre_editado)
            .first.get_attribute('value')
        )
        assert opcion_valor, 'La tarea creada no aparece en el selector de asignación'
        select_tarea.select_option(value=opcion_valor)

        modal_asignar.locator('button[type="submit"]').click()
        expect(page_admin.locator('.swal2-popup')).to_contain_text('Falta el destinatario')
        page_admin.locator('.swal2-confirm').click()

        modal_asignar.locator('#asig_usuarios').select_option(value=str(empleado.id))
        modal_asignar.locator('button[type="submit"]').click()
        page_admin.get_by_role('button', name=re.compile(r'S[ií], asignar', re.I)).click()
        expect(page_admin.locator('.swal2-popup')).to_contain_text('Operación exitosa')

        # 5. El empleado recibe la notificación y ve la tarea en "Mis Tareas".
        page_emp.goto(f'{url}/gestion-tarea/mis-tareas')
        tarjeta = page_emp.locator('.bento-card', has_text=nombre_editado).first
        expect(tarjeta).to_be_visible()

        badge_emp = page_emp.locator('#notifBadge')
        expect(badge_emp).to_be_visible()
        page_emp.locator('#btnNotificaciones').click()
        lista_notif_emp = page_emp.locator('#notifLista')
        expect(lista_notif_emp).not_to_contain_text('Cargando…')

        notif_asignada = lista_notif_emp.locator(
            '.notif-item.sin-leer', has_text=nombre_editado
        ).first
        expect(notif_asignada).to_be_visible()
        expect(notif_asignada.locator('.ni-titulo')).to_contain_text('Nueva tarea asignada')
        expect(notif_asignada.locator('.ni-mensaje')).to_contain_text(supervisor.nombre)
        page_emp.keyboard.press('Escape')

        # El rol "Usuario" debe poder completar sus propias tareas.
        tarjeta.locator('button[type="submit"]').click()
        expect(
            page_emp.locator('.bento-card', has_text=nombre_editado).first
        ).to_contain_text('Finalizada', timeout=15_000)

        # 6. El supervisor ve el estado y la notificación de conclusión.
        page_admin.goto(f'{url}/gestion-tarea/seguimiento')
        tabla_seg = page_admin.locator('#tablaSeguimiento')
        expect(tabla_seg).to_be_visible()

        fila_seg = tabla_seg.locator('tbody tr', has_text=nombre_editado).first
        expect(fila_seg).to_contain_text(empleado.nombre)
        expect(fila_seg).to_contain_text('Completada')

        badge_admin = page_admin.locator('#notifBadge')
        expect(badge_admin).to_be_visible()
        page_admin.locator('#btnNotificaciones').click()
        lista_notif_admin = page_admin.locator('#notifLista')
        expect(lista_notif_admin).not_to_contain_text('Cargando…')

        notif_completada = lista_notif_admin.locator(
            '.notif-item.sin-leer', has_text=nombre_editado
        ).first
        expect(notif_completada).to_be_visible()
        expect(notif_completada.locator('.ni-titulo')).to_contain_text('Tarea completada')
        expect(notif_completada.locator('.ni-mensaje')).to_contain_text(empleado.nombre)

        # 7. Limpieza de la tarea creada.
        page_admin.goto(f'{url}/gestion-tarea/')
        fila_final = tabla.locator('tbody tr', has_text=nombre_editado).first
        fila_final.locator('button[title="Eliminar"]').click()
        page_admin.get_by_role('button', name=re.compile(r'S[ií], eliminar', re.I)).click()
        expect(page_admin.locator('.swal2-popup')).to_contain_text('Tarea eliminada')
    finally:
        ctx_admin.close()
        ctx_emp.close()


def test_validacion_destinatario_sin_tarea_debe_mostrar_mensaje(
    browser, servidor, autenticar_contexto, crear_usuario_e2e
):
    """Regresión: el mensaje propio debe aparecer aunque falte la tarea.

    Hoy falla porque ``#formAsignarTarea`` no tiene ``novalidate`` y el
    ``<select required>`` de tarea dispara la validación nativa del navegador
    antes de que corra el handler que muestra "Falta el destinatario".
    """
    url = servidor['url']
    supervisor = crear_usuario_e2e(rol='Administrador', nombre='Validador UI')
    ctx = browser.new_context()
    autenticar_contexto(ctx, supervisor)
    page = ctx.new_page()

    try:
        page.goto(f'{url}/gestion-tarea/')
        page.locator('[data-bs-target="#modalAsignarTarea"]').click()
        modal = page.locator('#modalAsignarTarea')
        expect(modal).to_be_visible()
        expect(modal.locator('select[name="id_tarea"]')).to_have_value('')

        modal.locator('button[type="submit"]').click()
        expect(page.locator('.swal2-popup')).to_contain_text('Falta el destinatario')
    finally:
        ctx.close()
