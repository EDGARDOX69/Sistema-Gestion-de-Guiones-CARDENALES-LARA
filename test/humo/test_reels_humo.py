import os
import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5001"
REEL_BASE_NOMBRE = "Monitor Reel Prueba"
REEL_EDITADO_NOMBRE = "Monitor Reel Actualizado"


def _ir_a_reels(page: Page, ruta_relativa: str = "/reels/"):
    """Navega a la ruta indicada de reels asegurando que cargue el DOM."""
    url = f"{BASE_URL}{ruta_relativa}"
    page.goto(url, wait_until="domcontentloaded")
    if "/auth/login" in page.url:
        email = os.getenv("E2E_EMAIL")
        password = os.getenv("E2E_PASSWORD")
        if not email or not password:
            pytest.fail("Define E2E_EMAIL y E2E_PASSWORD para iniciar sesión en la prueba.")

        captcha = "".join(
            texto.strip() for texto in page.locator(".captcha-tile").all_text_contents()
        )
        if len(captcha) != 4:
            captcha = "ABCD"

        page.fill("#email", email)
        page.fill("#password", password)
        page.fill("#captcha_text", captcha)
        page.click("#btnLogin")
        expect(page).not_to_have_url(re.compile(r".*/auth/login"))
        page.goto(url, wait_until="domcontentloaded")


def _crear_reel_base(page: Page, nombre: str, duracion: str = "1,30", videos: list[dict] | None = None):
    """Responsabilidad única: crear un reel desde el formulario de /reels/crear."""
    _ir_a_reels(page, "/reels/crear")
    page.fill("input[name='nombre']", nombre)

    duracion_input = page.locator("input[name='duracion_total']")
    if duracion_input.count() > 0:
        duracion_input.first.fill(duracion)

    videos_a_agregar = videos or [{"nombre": "Video de prueba", "duracion": 30, "patrocinador": None}]
    for video in videos_a_agregar:
        page.locator("#agregarVideoBtn").click()
        fila_video = page.locator(".video-input-group").last
        fila_video.locator(".temp-nombre").fill(video["nombre"])

        minutos, segundos = divmod(int(video["duracion"]), 60)
        fila_video.locator(".temp-duracion").fill(f"{minutos},{segundos:02d}")

        patrocinador = video.get("patrocinador")
        if patrocinador is not None:
            fila_video.locator(".temp-patrocinador").select_option(str(patrocinador))
        fila_video.locator(".agregar-temp-video").click()

    page.click("button[type='submit'], input[type='submit']")
    page.get_by_role("button", name="Crear", exact=True).click()
    expect(page).to_have_url(re.compile(r".*/reels/?$"))


def _eliminar_reel_si_existe(page: Page, nombre: str):
    """Responsabilidad única: eliminar un reel del listado si aparece en pantalla."""
    _ir_a_reels(page, "/reels/")
    fila = page.locator("tr", has_text=nombre).first
    if fila.count() == 0:
        return

    delete_form = fila.locator("form[action*='/reels/eliminar/']").first
    if delete_form.count() > 0:
        delete_form.locator("button[type='submit'], input[type='submit']").first.click()
    else:
        fila.locator("button:has-text('Eliminar'), a:has-text('Eliminar')").first.click()
        confirm_btn = page.locator(
            "button:has-text('Confirmar'), button:has-text('Sí'), form[action*='/reels/eliminar/'] button"
        ).first
        if confirm_btn.count() > 0:
            confirm_btn.click()

    page.wait_for_load_state("domcontentloaded")


def test_smoke_dashboard_reels(page: Page):
    """
    Prueba de humo: Verifica que la ruta principal de reels responde
    y carga el dashboard correctamente.
    """
    _ir_a_reels(page, "/reels/")
    expect(page).to_have_url(re.compile(r".*/reels/?$"))

    header = page.locator("h1, h2, .card-title").filter(
        has_text=re.compile(r"reel|reels", re.IGNORECASE)
    )
    if header.count() > 0:
        expect(header.first).to_be_visible()


def test_crear_reel(page: Page):
    """
    Prueba de interfaz: Simula el registro de un nuevo reel
    a través del formulario en /reels/crear.
    """
    _eliminar_reel_si_existe(page, REEL_BASE_NOMBRE)

    _crear_reel_base(
        page,
        nombre=REEL_BASE_NOMBRE,
        duracion="1,30",
        videos=[{"nombre": "Spot Inicial", "duracion": 30, "patrocinador": None}],
    )

    expect(page.locator("body")).to_contain_text(REEL_BASE_NOMBRE)
    _eliminar_reel_si_existe(page, REEL_BASE_NOMBRE)


def test_ver_detalle_reel(page: Page):
    """
    Prueba E2E: Verifica la navegación y visualización
    del detalle de un reel específico.
    """
    _eliminar_reel_si_existe(page, REEL_BASE_NOMBRE)
    _crear_reel_base(page, nombre=REEL_BASE_NOMBRE)

    _ir_a_reels(page, "/reels/")
    detalle_link = page.locator("tr", has_text=REEL_BASE_NOMBRE).locator("a[href*='/reels/ver/']").first

    if detalle_link.count() > 0:
        detalle_link.click()
        expect(page).to_have_url(re.compile(r".*/reels/ver/\d+$"))
        expect(page.locator("body")).to_contain_text(REEL_BASE_NOMBRE)
    else:
        _ir_a_reels(page, "/reels/ver/1")
        expect(page).to_have_url(re.compile(r".*/reels/ver/1$"))

    _eliminar_reel_si_existe(page, REEL_BASE_NOMBRE)


def test_editar_reel(page: Page):
    """
    Prueba E2E: Verifica el flujo de edición de un reel existente
    modificando su nombre y guardando los cambios.
    """
    _eliminar_reel_si_existe(page, REEL_BASE_NOMBRE)
    _eliminar_reel_si_existe(page, REEL_EDITADO_NOMBRE)
    _crear_reel_base(page, nombre=REEL_BASE_NOMBRE)

    _ir_a_reels(page, "/reels/")
    editar_link = page.locator("tr", has_text=REEL_BASE_NOMBRE).locator("a[href*='/reels/editar/']").first

    if editar_link.count() > 0:
        editar_link.click()
        expect(page).to_have_url(re.compile(r".*/reels/editar/\d+$"))
    else:
        _ir_a_reels(page, "/reels/editar/1")
        expect(page).to_have_url(re.compile(r".*/reels/editar/1$"))

    nombre_input = page.locator("input[name='nombre']")
    nombre_input.fill(REEL_EDITADO_NOMBRE)

    page.click("button[type='submit'], input[type='submit']")
    page.get_by_role("button", name="Actualizar", exact=True).click()
    expect(page).to_have_url(re.compile(r".*/reels(/ver/\d+)?$"))
    expect(page.locator("body")).to_contain_text(REEL_EDITADO_NOMBRE)

    _eliminar_reel_si_existe(page, REEL_EDITADO_NOMBRE)


def test_eliminar_reel(page: Page):
    """
    Prueba E2E: Verifica la eliminación de un reel y que ya no aparezca
    en el listado principal.
    """
    _eliminar_reel_si_existe(page, REEL_BASE_NOMBRE)
    _crear_reel_base(page, nombre=REEL_BASE_NOMBRE)

    _eliminar_reel_si_existe(page, REEL_BASE_NOMBRE)
    _ir_a_reels(page, "/reels/")
    expect(page.locator("body")).not_to_contain_text(REEL_BASE_NOMBRE)