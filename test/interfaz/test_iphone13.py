from playwright.sync_api import sync_playwright

def test_emulacion_iphone13_simple():
    with sync_playwright() as p:
        # 1. Lanzar el navegador de forma visible
        browser = p.chromium.launch(headless=False)
        
        # 2. Obtener la configuración del iPhone 13 integrada en Playwright
        iphone_13 = p.devices["iPhone 13"]
        
        # 3. Crear el contexto aplicando las medidas y el perfil móvil
        context = browser.new_context(**iphone_13)
        page = context.new_page()
        
        # 4. Navegar a una página web de prueba pública
        page.goto("https://example.com")
        
        # 5. Mostrar en consola el tamaño de pantalla emulado
        print(f"¡Pantalla móvil emulada con éxito! Dimensiones: {page.viewport_size}")
        
        # Pausa corta opcional de 3 segundos para que alcances a ver el navegador en acción
        page.wait_for_timeout(3000)
        
        # 6. Cerrar el navegador
        browser.close()