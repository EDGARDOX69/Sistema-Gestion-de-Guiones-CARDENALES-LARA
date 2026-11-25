"""TA-UI — Flujo completo de tareas asignadas desde la interfaz.

Se ejecuta contra el servidor propio de `fixtures_e2e.py`, siempre sobre
``estadio_db_test`` y ``seguridad_test``:

    $env:E2E='1'; .venv\\Scripts\\python.exe -m pytest test/interfaz/test_tareas_asignadas.py -q

Cubre: asignar desde el modal, ver el estado en seguimiento, recibir la
notificación, completar desde "Mis Tareas" y confirmar el cambio en ambas vistas.
"""
import uuid

import pymysql
import pytest
from playwright.sync_api import expect

from soporte_pruebas import TEST_DBS, credenciales

pytestmark = pytest.mark.ui


def _conectar_bd(schema):
    """Conexión directa al esquema de prueba (el servidor E2E es otro proceso)."""
    return pymysql.connect(
        database=TEST_DBS[schema], autocommit=True, **credenciales()
    )


@pytest.fixture()
def tarea_ui():
    """Crea una tarea activa en ``estadio_db_test`` y la limpia al terminar."""
    creadas = []

    def _crear(id_creador):
        nombre = f'Tarea UI {uuid.uuid4().hex[:6]}'
        conn = _conectar_bd('estadio_db')
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO tareas
                       (Nombre_Tarea, Instruccion, id_usuario_creador, Estatus)
                       VALUES (%s, %s, %s, 1)""",
                    (nombre, 'Instrucción desde prueba UI', id_creador),
                )
                id_tarea = cur.lastrowid
        finally:
            conn.close()
        creadas.append(id_tarea)
        return {'id_tarea': id_tarea, 'Nombre_Tarea': nombre}

    yield _crear

    conn = _conectar_bd('estadio_db')
    try:
        with conn.cursor() as cur:
            for id_tarea in creadas:
                cur.execute('DELETE FROM tareas_asignadas WHERE id_tarea = %s', (id_tarea,))
                cur.execute('DELETE FROM tareas WHERE id_tarea = %s', (id_tarea,))
    finally:
        conn.close()


def _limpiar_notificaciones(ids_usuarios):
    conn = _conectar_bd('seguridad')
    try:
        with conn.cursor() as cur:
            cur.execute(
                'DELETE FROM notificaciones WHERE usuario_id IN (%s, %s)',
                tuple(ids_usuarios),
            )
    finally:
        conn.close()


def test_interfaz_asignar_seguimiento_y_completar_tarea(
    browser, servidor, autenticar_contexto, crear_usuario_e2e, tarea_ui
):
    """Un supervisor asigna, supervisa y el destinatario completa la tarea."""
    url = servidor['url']
    creador = crear_usuario_e2e(
        rol='Superadmin', nombre=f'Creador UI {uuid.uuid4().hex[:4]}'
    )
    # "Administrador" tiene gestion_tarea.view + gestion_tarea.complete;
    # el rol "Usuario" solo puede leer y no aparece escrito como "usuario".
    asignado = crear_usuario_e2e(
        rol='Administrador', nombre=f'Asignado UI {uuid.uuid4().hex[:4]}'
    )
    tarea = tarea_ui(id_creador=creador.id)

    ctx_creador = browser.new_context()
    ctx_asignado = browser.new_context()
    autenticar_contexto(ctx_creador, creador)
    autenticar_contexto(ctx_asignado, asignado)
    pagina_creador = ctx_creador.new_page()
    pagina_asignado = ctx_asignado.new_page()

    try:
        # 1. El creador asigna la tarea desde #modalAsignarTarea.
        pagina_creador.goto(f'{url}/gestion-tarea/')
        expect(pagina_creador.locator('#tablaTareas')).to_be_visible()
        pagina_creador.locator('button[data-bs-target="#modalAsignarTarea"]').click()

        modal = pagina_creador.locator('#modalAsignarTarea')
        expect(modal).to_be_visible()
        modal.locator('select[name="id_tarea"]').select_option(str(tarea['id_tarea']))
        modal.locator('#asig_usuarios').select_option(str(asignado.id))
        modal.locator('#formAsignarTarea button[type="submit"]').click()
        expect(pagina_creador.locator('.swal2-popup')).to_contain_text('¿Asignar tarea?')
        pagina_creador.locator('.swal2-confirm').click()
        expect(pagina_creador.locator('.swal2-popup')).to_contain_text('Operación exitosa')

        # 2. La asignación aparece pendiente en /gestion-tarea/seguimiento.
        pagina_creador.goto(f'{url}/gestion-tarea/seguimiento')
        fila_seg = pagina_creador.locator(
            '#tablaSeguimiento tbody tr', has_text=tarea['Nombre_Tarea']
        ).first
        expect(fila_seg).to_be_visible(timeout=10_000)
        expect(fila_seg).to_contain_text('Pendiente')
        expect(fila_seg).to_contain_text(asignado.nombre)

        # 3. El destinatario ve la tarea pendiente y la notificación de asignación.
        pagina_asignado.goto(f'{url}/gestion-tarea/mis-tareas')
        tarjeta = pagina_asignado.locator('.bento-card', has_text=tarea['Nombre_Tarea']).first
        expect(tarjeta).to_be_visible()
        expect(tarjeta).to_contain_text('Pendiente')

        expect(pagina_asignado.locator('#notifBadge')).not_to_have_attribute('hidden', '')
        pagina_asignado.locator('#btnNotificaciones').click()
        notif_asignada = pagina_asignado.locator(
            '.notif-item', has_text=tarea['Nombre_Tarea']
        ).first
        expect(notif_asignada.locator('.ni-titulo')).to_contain_text('Nueva tarea asignada')

        # 4. El destinatario la completa desde su panel.
        tarjeta.locator('button[type="submit"]').click()
        tarjeta_actualizada = pagina_asignado.locator(
            '.bento-card', has_text=tarea['Nombre_Tarea']
        ).first
        expect(tarjeta_actualizada).to_contain_text('Completada')
        expect(tarjeta_actualizada).to_contain_text('Finalizada')
        expect(tarjeta_actualizada.locator('button[type="submit"]')).to_have_count(0)

        # 5. El creador ve el cambio y la notificación de tarea completada.
        pagina_creador.goto(f'{url}/gestion-tarea/seguimiento')
        fila_final = pagina_creador.locator(
            '#tablaSeguimiento tbody tr', has_text=tarea['Nombre_Tarea']
        ).first
        expect(fila_final).to_be_visible()
        expect(fila_final).to_contain_text('Completada')

        expect(pagina_creador.locator('#notifBadge')).not_to_have_attribute('hidden', '')
        pagina_creador.locator('#btnNotificaciones').click()
        notif_completada = pagina_creador.locator(
            '.notif-item', has_text=tarea['Nombre_Tarea']
        ).first
        expect(notif_completada.locator('.ni-titulo')).to_contain_text('Tarea completada')
    finally:
        ctx_creador.close()
        ctx_asignado.close()
        _limpiar_notificaciones((creador.id, asignado.id))
