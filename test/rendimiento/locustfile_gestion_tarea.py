import csv
import os
import queue
import re
from pathlib import Path

from locust import HttpUser, between, task

CSV_CREDENCIALES = Path(__file__).with_name('usuario_locust.csv')
RUTA_SEGUIMIENTO = '/gestion-tarea/seguimiento'

# El token se genera en los formularios de las vistas. Se admiten ambos
# órdenes de atributos para no depender del orden de renderizado de Jinja.
CSRF_RE = re.compile(
    r'<input\b[^>]*\bname=["\']csrf_token["\'][^>]*\bvalue=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
CSRF_RE_INVERSO = re.compile(
    r'<input\b[^>]*\bvalue=["\']([^"\']+)["\'][^>]*\bname=["\']csrf_token["\']',
    re.IGNORECASE,
)


def extraer_csrf(html):
    """Devuelve el csrf_token renderizado en una vista, o None."""
    for patron in (CSRF_RE, CSRF_RE_INVERSO):
        encontrado = patron.search(html or '')
        if encontrado:
            return encontrado.group(1)
    return None


def _credenciales_csv():
    with CSV_CREDENCIALES.open('r', newline='', encoding='utf-8-sig') as archivo:
        # El CSV tiene una línea en blanco antes del encabezado.
        lineas = (linea for linea in archivo if linea.strip())
        return [
            (fila['email'].strip(), fila['password'].strip())
            for fila in csv.DictReader(lineas)
            if fila.get('email', '').strip() and fila.get('password', '').strip()
        ]


def cargar_credenciales():
    """Credenciales desde entorno (prioridad) o desde usuario_locust.csv."""
    password = os.environ.get('PERF_PASSWORD') or os.environ.get('E2E_PASSWORD')
    emails = [e.strip() for e in os.environ.get('PERF_EMAILS', '').split(',') if e.strip()]
    if emails and password:
        return [(email, password) for email in emails]

    email = os.environ.get('PERF_EMAIL') or os.environ.get('E2E_EMAIL')
    if email and password:
        return [(email, password)]

    if CSV_CREDENCIALES.exists():
        return _credenciales_csv()
    return []


_colas_credenciales = queue.Queue()
for _credencial in cargar_credenciales():
    _colas_credenciales.put(_credencial)


class TareaUser(HttpUser):
    """Operador que consulta el módulo de tareas."""

    # Predeterminado para poder arrancar sin --host; la CLI tiene prioridad.
    host = 'http://127.0.0.1:5001'
    wait_time = between(1, 3)

    def on_start(self):
        try:
            self.email, self.password = _colas_credenciales.get_nowait()
        except queue.Empty:
            raise RuntimeError(
                'No hay credenciales libres: usa una cuenta por usuario Locust '
                '(PERF_EMAILS / usuario_locust.csv).'
            )

        pagina_login = self.client.get('/auth/login', name='GET /auth/login')
        csrf_login = extraer_csrf(pagina_login.text)
        if not csrf_login:
            raise RuntimeError('No se pudo leer el CSRF del formulario de login')

        with self.client.post(
            '/auth/login',
            data={
                'csrf_token': csrf_login,
                'email': self.email,
                'password': self.password,
            },
            name='POST /auth/login',
            catch_response=True,
        ) as respuesta:
            login_correcto = '/dashboard' in respuesta.url
            if not login_correcto:
                respuesta.failure(
                    f'Login fallido para {self.email} (HTTP {respuesta.status_code})'
                )

        if not login_correcto:
            raise RuntimeError(f'Login fallido para {self.email}: revisar credenciales')

        # El POST ya sigue la redirección a /dashboard; esa misma vista trae el
        # csrf_token que usan los formularios y las tablas de tareas.
        html_dashboard = respuesta.text
        self.csrf_token = extraer_csrf(html_dashboard)
        if not self.csrf_token:
            panel = self.client.get('/dashboard', name='GET /dashboard')
            html_dashboard = panel.text
            self.csrf_token = extraer_csrf(html_dashboard)
        if not self.csrf_token:
            raise RuntimeError('No se pudo leer el CSRF del dashboard')

        # En /dashboard no aparece el enlace a Seguimiento: hay que mirar la
        # propia vista del módulo, que solo se renderiza con
        # gestion_tarea.supervisar. Así evitamos medir un redirect por permiso.
        modulo = self._get('/gestion-tarea/', 'GET /gestion-tarea/',
                           contiene='tablaTareas')
        self.puede_supervisar = RUTA_SEGUIMIENTO in modulo.text
        csrf_modulo = extraer_csrf(modulo.text)
        if csrf_modulo:
            self.csrf_token = csrf_modulo

    def _get(self, url, nombre, contiene=None):
        with self.client.get(url, name=nombre, catch_response=True) as res:
            if res.status_code != 200:
                res.failure(
                    f'[{self.email}] {nombre}: esperaba 200, obtuvo {res.status_code}'
                )
            elif contiene and contiene not in res.text:
                res.failure(
                    f'[{self.email}] {nombre}: la vista no contiene "{contiene}" '
                    '(¿sin permiso?)'
                )
            else:
                res.success()
        return res

    def _post_json(self, url, nombre, datos):
        with self.client.post(url, data=datos, name=nombre, catch_response=True) as res:
            try:
                payload = res.json()
            except ValueError:
                res.failure(f'[{self.email}] {nombre}: respuesta no JSON (HTTP {res.status_code})')
                return
            if res.status_code != 200:
                res.failure(
                    f'[{self.email}] {nombre}: esperaba 200, obtuvo {res.status_code}'
                )
            elif isinstance(payload, dict) and payload.get('error'):
                res.failure(f'[{self.email}] {nombre}: {payload["error"]}')
            elif not isinstance(payload, list):
                res.failure(f'[{self.email}] {nombre}: esperaba un array JSON')
            else:
                res.success()
        return res

    @task(1)
    def panel_principal(self):
        self._get('/dashboard', 'GET /dashboard')

    @task(4)
    def dashboard_tareas(self):
        self._get('/gestion-tarea/', 'GET /gestion-tarea/', contiene='tablaTareas')

    @task(3)
    def consultar_catalogo(self):
        # DataTables envía estos parámetros; el controlador solo usa 'consultar'
        # y el CSRF, pero se incluyen para acercarse al tráfico real.
        self._post_json('/gestion-tarea/', 'POST /gestion-tarea/ (consultar)', {
            'consultar': 'true',
            'csrf_token': self.csrf_token,
            'draw': '1',
            'start': '0',
            'length': '25',
        })

    @task(3)
    def mis_tareas(self):
        self._get('/gestion-tarea/mis-tareas', 'GET /gestion-tarea/mis-tareas',
                  contiene='Mis Tareas')

    @task(1)
    def seguimiento(self):
        if not self.puede_supervisar:
            return
        self._get('/gestion-tarea/seguimiento', 'GET /gestion-tarea/seguimiento',
                  contiene='tablaSeguimiento')

    @task(2)
    def consultar_asignaciones(self):
        if not self.puede_supervisar:
            return
        self._post_json(
            '/gestion-tarea/consultar-asignaciones',
            'POST /gestion-tarea/consultar-asignaciones',
            {
                'csrf_token': self.csrf_token,
                'draw': '1',
                'start': '0',
                'length': '25',
            },
        )
