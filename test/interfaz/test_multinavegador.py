# Demuestra las pruebas Multi-navegador y Móvil con estos comandos:

# 1. chromium
# Bash
# -m pytest test/interface/test_multinavegador.py --browser chromium --headed -s

# 2. En Firefox:
# Bash
# python -m pytest tests/interface/test_multinavegador.py --browser firefox --headed -s

# 3. En WebKit (Safari):
# Bash
# python -m pytest tests/interface/test_multinavegador.py --browser webkit --headed -s



def test_verificar_titulo(page):
    page.goto("https://example.com")
    assert "Example Domain" in page.title()