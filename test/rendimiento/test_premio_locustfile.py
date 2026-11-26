#  python -m locust -f test/rendimiento/test_premio_locustfile.py --headless -u 20 -r 5 --run-time 15s --host http://127.0.0.1:5001

# python -m locust -f test/rendimiento/test_premio_locustfile.py --host=http://127.0.0.1:5001 

import re
from locust import HttpUser, task, between

class UsuarioPremioRendimiento(HttpUser):
    wait_time = between(1, 2)
    csrf_token = ""

    def on_start(self):
        # Obtenemos la página inicial para extraer el csrf_token si existe
        resp = self.client.get("/premio/")
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', resp.text)
        if match:
            self.csrf_token = match.group(1)

    @task(3)
    def ver_dashboard_premios(self):
        self.client.get("/premio/")

    @task(1)
    def consultar_catalogo_premios_post(self):
        payload = {"accion": "consultar"}
        if self.csrf_token:
            payload["csrf_token"] = self.csrf_token
        with self.client.post("/premio/", data=payload, catch_response=True) as resp:
            if resp.status_code in [200, 401]:
                resp.success()