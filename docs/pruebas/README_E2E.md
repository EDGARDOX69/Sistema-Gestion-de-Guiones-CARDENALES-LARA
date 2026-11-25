# Pruebas end-to-end con Playwright y pytest

Pruebas del sistema Itinerario en un navegador real. Viven en `test/interfaz/`
dentro de la carpeta única de pruebas. No se modifica nada de `app/`, `run.py`
ni del resto de la suite.

## Requisitos

- Python del proyecto (`venv/`).
- MySQL encendido y el archivo `.env` configurado en la raíz.
- El servidor Flask no hay que levantarlo a mano: `conftest.py` lo arranca y lo
  apaga alrededor de la ejecución.

## Instalación

```bash
source venv/bin/activate        # desde la raíz del proyecto
pip install -r test/interfaz/requirements.txt
python -m playwright install chromium
```

## Ejecución

La carpeta está ignorada en la corrida normal (`pytest` desde la raíz). Se
activa con `E2E=1` para no exigir navegador ni servidor cuando solo se prueban
modelos o rutas:

```bash
E2E=1 venv/bin/pytest test/interfaz              # suite completa
E2E=1 venv/bin/pytest test/interfaz --headed     # con el navegador visible
E2E=1 venv/bin/pytest test/interfaz -k login     # solo el flujo de acceso
E2E=1 venv/bin/pytest test/interfaz --browser firefox
```

El reporte HTML queda en `test/interfaz/reporte.html` y los artefactos de los
fallos en `test/interfaz/test-results/`.

## Estructura

```
test/interfaz/
├── pytest.ini          # configuración de pytest y de Playwright
├── conftest.py         # levanta el servidor Flask y controla el gate E2E
├── requirements.txt
├── test_login.py       # flujo público de acceso
└── test_guion_ui.py    # interfaz del módulo guion (requiere credenciales)
```

## Qué se prueba

- La raíz redirige al login.
- El formulario muestra correo y contraseña, sin CAPTCHA.
- La pantalla de recuperación de contraseña carga sin CAPTCHA.
- El login con credenciales llega al dashboard (opcional).
- El módulo guion: dashboard, formulario de creación y previsualización
  (opcional, con `E2E_EMAIL` / `E2E_PASSWORD`).

## Sobre el CAPTCHA

El CAPTCHA está desactivado por defecto (`CAPTCHA_ENABLED=0`). Cuando se activa
con `CAPTCHA_ENABLED=1`, sus cuatro caracteres están en el DOM dentro de
`.captcha-tile` y los helpers de login los leen de la página solo si el campo
existe. La validación del modo activo se comprueba en
`test/integracion/test_auth.py`.

## Evidencia ante fallos

Con `--tracing`, `--video` y `--screenshot` en `retain-on-failure`, cada prueba
que falla deja en `test-results/` una captura, un video y un `trace.zip`:

```bash
venv/bin/playwright show-trace test/interfaz/test-results/<carpeta>/trace.zip
```
