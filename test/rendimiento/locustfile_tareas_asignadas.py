import csv
import itertools
import re
from pathlib import Path

from locust import HttpUser, between, task

CSV_CREDENCIALES = Path(__file__).with_name("usuario_locust.csv")

CSRF_RE = re.compile(
    r'<input\b[^>]*\bname=["\']csrf_token["\'][^>]*\bvalue=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
CSRF_RE_INVERSO = re.compile(
    r'<input\b[^>]*\bvalue=["\']([^"\']+)["\'][^>]*\bname=["\']csrf_token["\']',
    re.IGNORECASE,
)


def extraer_csrf(html):
    for patron in (CSRF_RE, CSRF_RE_INVERSO):
        encontrado = patron.search(html or "")
        if encontrado:
            return encontrado.group(1)
    return None


def cargar_usuarios():
    if not CSV_CREDENCIALES.exists():
        return []
    with CSV_CREDENCIALES.open("r", newline="", encoding="utf-8-sig") as archivo:
        lineas = (linea for linea in archivo if linea.strip())
        return [
            (fila["email"].strip(), fila["password"].strip())
            for fila in csv.DictReader(lineas)
            if fila.get("email", "").strip() and fila.get("password", "").strip()
        ]


_ciclo_usuarios = itertools.cycle(cargar_usuarios())


class TareasAsignadasUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://127.0.0.1:5001"

    def on_start(self):
        self.email, self.password = next(_ciclo_usuarios)

        login_get = self.client.get("/auth/login", name="GET /auth/login")
        csrf = extraer_csrf(login_get.text)

        with self.client.post(
            "/auth/login",
            data={
                "csrf_token": csrf,
                "email": self.email,
                "password": self.password,
            },
            name="POST /auth/login",
            catch_response=True,
        ) as res:
            if res.status_code not in (200, 302) or "/dashboard" not in res.url:
                res.failure(f"[{self.email}] Falló el login (HTTP {res.status_code})")
            else:
                res.success()

        self.csrf_token = extraer_csrf(res.text) or csrf

    @task(3)
    def ver_tareas_asignadas(self):
        # Ajusta la ruta si tu vista se llama distinto (ej. "/gestion-tarea/mis-tareas")
        with self.client.get(
            "/gestion-tarea/mis-tareas",
            name="GET /gestion-tarea/mis-tareas",
            catch_response=True,
        ) as res:
            token = extraer_csrf(res.text)
            if token:
                self.csrf_token = token
            if res.status_code != 200:
                res.failure(
                    f"[{self.email}] Esperaba 200 en tareas asignadas, obtuvo {res.status_code}"
                )
            else:
                res.success()

    @task(2)
    def consultar_asignaciones(self):
        # Ajusta el endpoint o payload según tu controlador de asignaciones
        with self.client.post(
            "/gestion-tarea/consultar-asignaciones",
            data={
                "csrf_token": self.csrf_token,
                "draw": "1",
                "start": "0",
                "length": "25",
            },
            name="POST /gestion-tarea/consultar-asignaciones",
            catch_response=True,
        ) as res:
            if res.status_code != 200:
                res.failure(
                    f"[{self.email}] Falló consulta de asignaciones (HTTP {res.status_code})"
                )
            else:
                res.success()