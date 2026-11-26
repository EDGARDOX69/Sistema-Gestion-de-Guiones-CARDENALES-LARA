import os
import random
from html.parser import HTMLParser

from locust import HttpUser, task, between


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


class InventarioTiposUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.csrf_token = None
        self.tipos_creados = []  # Guardamos los IDs de los tipos creados para luego editarlos/eliminarlos
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

        # Actualiza el token ya autenticado
        self._refresh_csrf("/inventario/")

    @task(4)
    def consultar_tipos(self):
        """Simula la carga de la tabla de tipos de activos."""
        self._refresh_csrf("/inventario/")
        self.client.post(
            "/inventario/",
            data={
                "consultar_tipos": "1",
                "csrf_token": self.csrf_token,
            },
            name="POST /inventario/ (consultar_tipos)",
        )

    @task(2)
    def agregar_tipo(self):
        """Simula la creación de un nuevo tipo de activo."""
        self._refresh_csrf("/inventario/")
        n = random.randint(1000, 999999)
        nombre_tipo = f"Tipo Locust {n}"
        
        response = self.client.post(
            "/inventario/",
            data={
                "agregar_tipo_activo": "1",
                "nombre_tipo_activo": nombre_tipo,
                "descripcion_tipo_activo": "Prueba de rendimiento automatizada",
                "csrf_token": self.csrf_token,
            },
            name="POST /inventario/ (agregar_tipo)",
        )
        
        # Nota: Dependiendo de cómo devuelva el ID tu backend (en el JSON o en la sesión),
        # podríamos guardar el ID para luego probar editar/eliminar. 
        # Si tu endpoint actual no devuelve el ID, el test de editar/eliminar usará un ID aleatorio.

    @task(1)
    def buscar_tipo(self):
        """Simula la búsqueda de un tipo de activo."""
        self._refresh_csrf("/inventario/")
        # Usamos un ID aleatorio del 1 al 20 (asumiendo que existen)
        id_tipo = random.randint(1, 20)
        self.client.post(
            "/inventario/",
            data={
                "buscar_tipos": "1",
                "idTipo": str(id_tipo),
                "csrf_token": self.csrf_token,
            },
            name="POST /inventario/ (buscar_tipos)",
        )

    @task(1)
    def editar_tipo(self):
        """Simula la edición de un tipo de activo existente."""
        self._refresh_csrf("/inventario/")
        # Usamos un ID aleatorio (ajusta el rango según los IDs reales de tu BD)
        id_tipo = random.randint(1, 20)
        n = random.randint(1000, 999999)
        
        self.client.post(
            "/inventario/",
            data={
                "editar_tipo_activo": str(id_tipo),
                "nombre_tipo_activo": f"Tipo Editado Locust {n}",
                "descripcion_tipo_activo": "Descripción editada por Locust",
                "csrf_token": self.csrf_token,
            },
            name="POST /inventario/ (editar_tipo)",
        )

    @task(1)
    def eliminar_tipo(self):
        """Simula la eliminación de un tipo de activo."""
        self._refresh_csrf("/inventario/")
        # OJO: Si envías un ID que no existe o que tiene activos asociados, 
        # tu backend devolverá "Error al eliminar". Para pruebas de carga 
        # está bien, pero ten cuidado con la BD de pruebas.
        id_tipo = random.randint(1, 20) 
        
        self.client.post(
            "/inventario/",
            data={
                "eliminar_tipo_activo": str(id_tipo),
                "csrf_token": self.csrf_token,
            },
            name="POST /inventario/ (eliminar_tipo)",
        )