"""GU-PF — Prueba de rendimiento del módulo guion con Locust.

No la ejecuta pytest. Se corre aparte, con el servidor levantado:

    venv/bin/locust -f test/rendimiento/locustfile.py --headless \
        -u 30 -r 5 -t 60s --host http://127.0.0.1:5001

Credenciales: PERF_EMAIL / PERF_PASSWORD (o E2E_EMAIL / E2E_PASSWORD).
Opcional: PERF_GUION_ID para medir previsualización y estado de EN VIVO.

Criterio de aceptación sugerido (ajustar con el equipo):
- 0 % de errores HTTP con 30 usuarios concurrentes durante 60 s.
- p95 del dashboard de guiones por debajo de 800 ms en local.
"""
import os
import queue
import re

from locust import HttpUser, between, task

EMAIL = os.environ.get('PERF_EMAIL') or os.environ.get('E2E_EMAIL')
PASSWORD = os.environ.get('PERF_PASSWORD') or os.environ.get('E2E_PASSWORD')
GUION_ID = os.environ.get('PERF_GUION_ID')

# Para pruebas concurrentes: una cuenta por usuario (el sistema fuerza sesión
# única, así que 30 usuarios con la misma cuenta se expulsarían entre sí).
EMAILS = [e.strip() for e in os.environ.get('PERF_EMAILS', '').split(',') if e.strip()]
_email_queue = queue.Queue()
for _email in EMAILS:
    _email_queue.put(_email)


def _email_de_turno():
    try:
        return _email_queue.get_nowait()
    except queue.Empty:
        return EMAIL

CSRF = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')


class GuionUser(HttpUser):
    """Un operador que consulta guiones durante el show."""

    wait_time = between(1, 3)

    def on_start(self):
        email = _email_de_turno()
        if not (email and PASSWORD):
            raise RuntimeError('Definir PERF_EMAIL(S) y PERF_PASSWORD para la prueba de carga')

        login = self.client.get('/auth/login')
        token = CSRF.search(login.text)
        if not token:
            raise RuntimeError('No se pudo leer el CSRF del login')

        respuesta = self.client.post('/auth/login', data={
            'csrf_token': token.group(1),
            'email': email,
            'password': PASSWORD,
        })
        if '/dashboard' not in respuesta.url:
            raise RuntimeError(f'Login fallido para {email}: revisar credenciales')

    @task(3)
    def dashboard_guiones(self):
        self.client.get('/guiones/', name='/guiones/')

    @task(1)
    def pantalla_crear(self):
        self.client.get('/guiones/crear', name='/guiones/crear')

    @task(2)
    def previsualizar(self):
        if GUION_ID:
            self.client.get(
                f'/guiones/previsualizar/{GUION_ID}',
                name='/guiones/previsualizar/[id]',
            )

    @task(2)
    def estado_en_vivo(self):
        if GUION_ID:
            self.client.get(
                f'/en-vivo/api/estado-actual/{GUION_ID}',
                name='/en-vivo/api/estado-actual/[id]',
            )
