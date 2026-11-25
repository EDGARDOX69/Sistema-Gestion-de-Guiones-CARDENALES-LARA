"""Pruebas end-to-end del flujo público de acceso a Itinerario.

El CAPTCHA viene desactivado por defecto (``CAPTCHA_ENABLED=0``), así que el
formulario solo pide correo y contraseña. La cobertura del modo activo está en
`test/integracion/test_auth.py`.
"""
import os
import re

import pytest
from playwright.sync_api import Page, expect


def test_raiz_redirige_al_login(page: Page):
    page.goto("/")
    expect(page).to_have_url(re.compile(r"/auth/login$"))
    expect(
        page.get_by_role("heading", name=re.compile(r"Iniciar\s+Sesi[oó]n", re.I))
    ).to_be_visible()


def test_formulario_muestra_campos(page: Page):
    page.goto("/auth/login")
    expect(page.locator("#email")).to_be_visible()
    expect(page.locator("#password")).to_be_visible()
    expect(page.locator("#btnLogin")).to_be_visible()
    expect(page.locator(".captcha-tile")).to_have_count(0)
    expect(page.locator("#captcha_text")).to_have_count(0)


def test_pantalla_recuperar_password_carga(page: Page):
    page.goto("/auth/forgot-password")
    expect(
        page.get_by_role("heading", name=re.compile(r"Recuperar\s+Contrase[ñn]a", re.I))
    ).to_be_visible()
    expect(page.locator('input[name="email"]')).to_be_visible()
    expect(page.locator("#btnSend")).to_be_visible()
    expect(page.locator("#captcha_text")).to_have_count(0)


EMAIL = os.environ.get("E2E_EMAIL")
PASSWORD = os.environ.get("E2E_PASSWORD")


@pytest.mark.skipif(
    not (EMAIL and PASSWORD),
    reason="Definir E2E_EMAIL y E2E_PASSWORD para ejecutar el login real",
)
def test_login_con_credenciales_llega_al_dashboard(page: Page):
    page.goto("/auth/login")
    page.fill("#email", EMAIL)
    page.fill("#password", PASSWORD)
    page.click("#btnLogin")

    page.wait_for_url(re.compile(r"/dashboard"), timeout=30_000)
