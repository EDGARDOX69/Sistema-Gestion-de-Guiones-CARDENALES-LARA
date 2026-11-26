import os
import random
from html.parser import HTMLParser

from locust import HttpUser, task, between
# from locust import LoadTestShape  # Descomenta si vuelves a usar la clase del final

class CSRFTokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "input":
            return
        attributes = dict(attrs)
        if attributes.get("name") == "csrf_token":
            self.token = attributes.get("value")


class InventarioUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.csrf_token = None
        self._login()

    def _extraer_token(self, html_text):
        parser = CSRFTokenParser()
        parser.feed(html_text)
        return parser.token

    def _refresh_csrf(self, ruta="/inventario/"):
        """Obtiene un token CSRF fresco desde la ruta indicada."""
        response = self.client.get(ruta, name=f"GET {ruta} (CSRF)")
        token = self._extraer_token(response.text)
        if not token:
            raise RuntimeError(f"No se encontró el token CSRF en {ruta}")
        self.csrf_token = token
        return token

    def _login(self):
        """Obtiene el token de /auth/login e inicia sesión."""
        resp_get = self.client.get("/auth/login", name="GET /auth/login (CSRF)")
        token = self._extraer_token(resp_get.text)
        if not token:
            raise RuntimeError("No se encontró el token CSRF en /auth/login")

        # Ajusta los nombres de campos según tu formulario real
        usuario = os.getenv("LOCUST_USER", "superadmin")
        password = os.getenv("LOCUST_PASS", "123456")

        resp_post = self.client.post(
            "/auth/login",
            data={
                "usuario": usuario,
                "password": password,
                "csrf_token": token,
            },
            name="POST /auth/login",
            allow_redirects=True,
        )
        if resp_post.status_code >= 400:
            raise RuntimeError(f"Error en login: {resp_post.status_code}")

        # Actualiza el token ya autenticado en /inventario/
        self._refresh_csrf("/inventario/")

    @task(3)
    def ver_dashboard_get(self):
        self.client.get("/inventario/", name="GET /inventario/")

    @task(3)
    def consultar_activos_post(self):
        self._refresh_csrf("/inventario/")
        self.client.post(
            "/inventario/",
            data={
                "consultar": "1",
                "csrf_token": self.csrf_token,
            },
            name="POST /inventario/ (consultar)",
        )

    @task(1)
    def registrar_activo_post(self):
        self._refresh_csrf("/inventario/")
        n = random.randint(1000, 999999)
        self.client.post(
            "/inventario/",
            data={
                "registrar": "1",
                "id_tipo_activo": "1",
                "Nombre": f"Activo Locust {n}",
                "Descripcion": "Prueba de rendimiento con Locust",
                "Fecha_adquisicion": "2026-11-18",
                "csrf_token": self.csrf_token,
            },
            name="POST /inventario/ (registrar)",
        )


# -------------------------------------------------------------------------
# CLASE COMENTADA: Al quitarla, Locust te permite escribir los usuarios 
# manualmente en la interfaz web (http://localhost:8089).
# -------------------------------------------------------------------------
# class ProgressiveLoadShape(LoadTestShape):
#     """
#     - Sube de 1 a 50 usuarios en 100 segundos.
#     - Mantiene 50 usuarios de 100 a 220 segundos.
#     - Baja a 0 de 220 a 280 segundos.
#     """
#     time_limit = 280
#
#     def tick(self):
#         run_time = self.get_run_time()
#
#         if run_time > self.time_limit:
#             return None
#
#         if run_time < 100:
#             user_count = max(1, int(run_time * 0.5))
#             return (user_count, 1)
#
#         elif run_time < 220:
#             return (50, 1)
#
#         else:
#             remaining_time = self.time_limit - run_time
#             user_count = max(0, int(remaining_time * (50 / 60)))
#             return (user_count, 1)