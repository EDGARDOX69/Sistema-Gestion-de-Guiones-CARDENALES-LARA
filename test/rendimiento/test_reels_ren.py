from html.parser import HTMLParser
from itertools import count
import json
import logging
import os
import random
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from locust import HttpUser, task, between, tag, events
from werkzeug.security import generate_password_hash


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")
logger = logging.getLogger(__name__)
_user_indices = count(1)


def _provisionar_usuarios():
    password = os.getenv("LOCUST_REELS_PASSWORD")
    if not password:
        raise RuntimeError("Define LOCUST_REELS_PASSWORD antes de iniciar la prueba")

    pool_size = int(os.getenv("LOCUST_REELS_USER_POOL_SIZE", "100"))
    if not 1 <= pool_size <= 1000:
        raise RuntimeError("LOCUST_REELS_USER_POOL_SIZE debe estar entre 1 y 1000")

    database = os.getenv("DB_NAME_SEGURIDAD", "seguridad_test")
    if not database.endswith("_test"):
        raise RuntimeError(
            "Locust solo puede crear cuentas en una base terminada en _test; "
            "configura DB_NAME_SEGURIDAD=seguridad_test"
        )

    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=database,
        charset="utf8mb4",
        autocommit=False,
    )
    password_hash = generate_password_hash(password)
    rows = [
        (
            f"Locust Reels {index:04d}",
            f"locust_reels_{index:04d}@loadtest.invalid",
            password_hash,
            f"LOCUST{index:08d}",
        )
        for index in range(1, pool_size + 1)
    ]
    try:
        with connection.cursor() as cursor:
            cursor.executemany(
                """INSERT INTO usuarios
                   (nombre, email, password_hash, cedula, rol, departamento,
                    telefono, activo, fecha_registro)
                   VALUES (%s, %s, %s, %s, 'Superadmin', 'Medios', NULL, 1, NOW())
                   ON DUPLICATE KEY UPDATE
                     password_hash = VALUES(password_hash),
                     rol = VALUES(rol), activo = 1""",
                rows,
            )
        connection.commit()
    except Exception:
        connection.rollback()
        logger.exception("No se pudo preparar el pool de usuarios de Locust")
        raise
    finally:
        connection.close()

    logger.info("Pool de %s usuarios preparado en %s", pool_size, database)


@events.init.add_listener
def preparar_pool_locust(environment, **kwargs):
    _provisionar_usuarios()


@events.test_start.add_listener
def reiniciar_indices_usuarios(environment, **kwargs):
    global _user_indices
    _user_indices = count(1)


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


class ReelsUsuario(HttpUser):
    wait_time = between(1, 3)
    created_reel_ids = []

    def on_start(self):
        self.created_reel_ids = []
        user_index = next(_user_indices)
        pool_size = int(os.getenv("LOCUST_REELS_USER_POOL_SIZE", "100"))
        if user_index > pool_size:
            raise RuntimeError(
                "El número de usuarios virtuales supera LOCUST_REELS_USER_POOL_SIZE"
            )

        email = f"locust_reels_{user_index:04d}@loadtest.invalid"
        password = os.getenv("LOCUST_REELS_PASSWORD")
        if not password:
            raise RuntimeError("Define LOCUST_REELS_PASSWORD antes de iniciar Locust")

        login_page = self.client.get("/auth/login", name="GET /auth/login (CSRF)")
        parser = CSRFTokenParser()
        parser.feed(login_page.text)
        if login_page.status_code != 200 or not parser.token:
            raise RuntimeError("No se pudo obtener el token CSRF del formulario de login")

        response = self.client.post(
            "/auth/login",
            data={
                "email": email,
                "password": password,
                "csrf_token": parser.token,
            },
            name="POST /auth/login",
            allow_redirects=True,
        )
        if response.status_code != 200 or response.url.rstrip("/").endswith("/auth/login"):
            raise RuntimeError("Login fallido; verifica las credenciales de Locust")

    def _obtener_csrf(self, ruta="/reels/crear"):
        resp = self.client.get(ruta, name=f"GET {ruta} (csrf)")
        parser = CSRFTokenParser()
        parser.feed(resp.text)
        if resp.status_code != 200 or not parser.token:
            raise RuntimeError(f"No se pudo obtener CSRF válido desde {ruta}")
        return parser.token

    def _post_con_csrf(self, url, payload, ruta_csrf="/reels/crear", **kwargs):
        token = self._obtener_csrf(ruta_csrf)
        data = dict(payload)
        data["csrf_token"] = token
        return self.client.post(url, data=data, **kwargs)

    @task(4)
    @tag("lectura", "dashboard")
    def ver_dashboard_html(self):
        with self.client.get(
            "/reels/",
            name="GET /reels/ (dashboard)",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error en dashboard HTML: {response.status_code}")

    @task(3)
    @tag("lectura", "api")
    def consultar_reels_json(self):
        with self._post_con_csrf(
            "/reels/",
            {"consultar": "1"},
            ruta_csrf="/reels/",
            name="POST /reels/ (consultar JSON)",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        if not self.created_reel_ids and data:
                            sample_ids = [item["id"] for item in data if "id" in item]
                            self.created_reel_ids.extend(sample_ids[:5])
                        response.success()
                    else:
                        response.failure("La respuesta JSON no es una lista")
                except ValueError:
                    response.failure("Respuesta no es JSON válido")
            else:
                snippet = response.text[:200].replace("\n", " ")
                response.failure(
                    f"Error consultando JSON: {response.status_code} | {snippet}"
                )

    @task(2)
    @tag("lectura", "detalle")
    def ver_detalle_reel(self):
        reel_id = self._obtener_reel_id()
        if not reel_id:
            return
        with self.client.get(
            f"/reels/ver/{reel_id}",
            name="GET /reels/ver/<id>",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error al ver reel {reel_id}: {response.status_code}")

    @task(2)
    @tag("escritura", "crear")
    def crear_reel(self):
        idx = random.randint(1, 999999)
        videos = [
            {
                "nombre": f"Spot Promo {idx}-1",
                "duracion": random.choice([15, 20, 30]),
                "patrocinador": None,
            },
            {
                "nombre": f"Spot Promo {idx}-2",
                "duracion": random.choice([10, 15, 25]),
                "patrocinador": None,
            },
        ]
        payload = {
            "nombre": f"Reel Carga {idx}",
            "duracion_total": random.choice(["1,00", "1,30", "2,15", "3"]),
            "videos_json": json.dumps(videos),
        }

        with self._post_con_csrf(
            "/reels/crear",
            payload,
            ruta_csrf="/reels/crear",
            name="POST /reels/crear",
            allow_redirects=True,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
                self._sincronizar_ultimo_reel_id()
            else:
                snippet = response.text[:200].replace("\n", " ")
                response.failure(
                    f"Error al crear reel: {response.status_code} | {snippet}"
                )

    @task(2)
    @tag("escritura", "video")
    def agregar_video_a_reel(self):
        reel_id = self._obtener_reel_id()
        if not reel_id:
            return

        payload = {
            "nombre": f"Video Extra {random.randint(1, 10000)}",
            "duracion_segundos": str(random.choice([10, 15, 30, 45])),
            "orden": str(random.randint(1, 10)),
        }

        with self._post_con_csrf(
            f"/reels/{reel_id}/agregar-video",
            payload,
            ruta_csrf=f"/reels/ver/{reel_id}",
            name="POST /reels/<reel_id>/agregar-video",
            allow_redirects=True,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Error agregando video al reel {reel_id}: {response.status_code}"
                )

    @task(1)
    @tag("escritura", "editar")
    def editar_reel(self):
        reel_id = self._obtener_reel_id()
        if not reel_id:
            return

        videos_actualizados = [
            {
                "nombre": f"Clip Editado {random.randint(1, 5000)}",
                "duracion": 20,
                "patrocinador": None,
            }
        ]
        payload = {
            "nombre": f"Reel Editado {reel_id}",
            "duracion_total": "0,20",
            "videos_json": json.dumps(videos_actualizados),
        }

        with self._post_con_csrf(
            f"/reels/editar/{reel_id}",
            payload,
            ruta_csrf=f"/reels/editar/{reel_id}",
            name="POST /reels/editar/<id>",
            allow_redirects=True,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error editando reel {reel_id}: {response.status_code}")

    def _obtener_reel_id(self):
        if self.created_reel_ids:
            return random.choice(self.created_reel_ids)
        return None

    def _sincronizar_ultimo_reel_id(self):
        """Consulta el endpoint JSON para obtener el ID más reciente y probar rutas con <int:id>."""
        resp = self._post_con_csrf(
            "/reels/",
            {"consultar": "1"},
            ruta_csrf="/reels/",
            name="POST /reels/ (sync id)",
        )
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data and isinstance(data, list):
                    ultimo_id = data[-1].get("id")
                    if ultimo_id and ultimo_id not in self.created_reel_ids:
                        self.created_reel_ids.append(ultimo_id)
                        if len(self.created_reel_ids) > 20:
                            self.created_reel_ids.pop(0)
            except ValueError:
                pass