"""Utilidades compartidas por las pruebas de interfaz por modulo."""

import re

from playwright.sync_api import Page, expect


def login(page: Page, credenciales) -> None:
    """Inicia sesion; lee el CAPTCHA del DOM solo si esta activo."""
    page.goto('/auth/login')
    if page.locator('#captcha_text').count():
        tiles = page.locator('.captcha-tile')
        expect(tiles).to_have_count(4)
        codigo = ''.join(texto.strip() for texto in tiles.all_text_contents())
        page.fill('#captcha_text', codigo)

    page.fill('#email', credenciales['email'])
    page.fill('#password', credenciales['password'])
    page.click('#btnLogin')
    page.wait_for_url(
        re.compile(r'/dashboard'),
        timeout=30_000,
        wait_until='domcontentloaded',
    )
