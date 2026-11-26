import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("APP_URL", "http://127.0.0.1:5001")
VALID_EMAIL = os.environ.get("E2E_EMAIL", "admin@admin.com")
VALID_PASSWORD = os.environ.get("E2E_PASSWORD", "admin123")
INVALID_PASSWORD = os.environ.get("E2E_INVALID_PASSWORD", "clave_incorrecta_999")


def test_auth_01_login_exitoso_y_redireccion_dashboard(page: Page):
    """Valida inicio de sesión con credenciales válidas y redirección al dashboard."""
    page.goto(f"{BASE_URL}/auth/login", wait_until="domcontentloaded")
    page.fill('input[name="email"]', VALID_EMAIL)
    page.fill('input[name="password"]', VALID_PASSWORD)
    page.click('button[type="submit"]')

    page.wait_for_url(f"{BASE_URL}/dashboard**", timeout=10000)
    expect(page.locator("body")).not_to_contain_text("Email o contraseña incorrectos")


def test_auth_02_rechazo_credenciales_invalidas(page: Page):
    """Valida que credenciales inválidas no inicien sesión y muestren alerta de error."""
    page.goto(f"{BASE_URL}/auth/login", wait_until="domcontentloaded")
    page.fill('input[name="email"]', VALID_EMAIL)
    page.fill('input[name="password"]', INVALID_PASSWORD)
    page.click('button[type="submit"]')

    expect(page).to_have_url(f"{BASE_URL}/auth/login", timeout=10000)
    expect(page.locator(".alert")).to_contain_text("Email o contraseña incorrectos")


def test_auth_03_acceso_ruta_protegida_sin_sesion_redirige_login(page: Page):
    """Valida que ingresar a una ruta protegida sin sesión redirija a /auth/login."""
    page.context.clear_cookies()
    page.goto(f"{BASE_URL}/dashboard", wait_until="domcontentloaded")
    expect(page).to_have_url(f"{BASE_URL}/auth/login**", timeout=10000)


def test_auth_04_cierre_sesion_logout(page: Page):
    """Abre el menú del usuario desde el dropdown-toggle y cierra sesión."""
    page.goto(f"{BASE_URL}/auth/login", wait_until="domcontentloaded")
    page.fill('input[name="email"]', VALID_EMAIL)
    page.fill('input[name="password"]', VALID_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{BASE_URL}/dashboard**", timeout=10000)

    # 1. Abrir el dropdown del usuario (Admin + fa-user-circle)
    dropdown_usuario = page.locator('a.dropdown-toggle[data-bs-toggle="dropdown"]', has=page.locator('.fa-user-circle'))
    dropdown_usuario.click()
    expect(dropdown_usuario).to_have_attribute("aria-expanded", "true", timeout=5000)

    # 2. Hacer clic en "Cerrar Sesion" dentro del menú desplegado
    opcion_logout = page.locator('a[href*="/auth/logout"], a:has-text("Cerrar Sesion")').first
    expect(opcion_logout).to_be_visible(timeout=5000)
    opcion_logout.click()

    alerta = page.locator('div.alert[role="alert"]')
    expect(alerta).to_be_visible(timeout=5000)
    expect(alerta).to_contain_text("Sesión cerrada correctamente")
    
    page.goto(f"{BASE_URL}/dashboard", wait_until="domcontentloaded")
    expect(page).to_have_url(f"{BASE_URL}/auth/login**", timeout=10000)