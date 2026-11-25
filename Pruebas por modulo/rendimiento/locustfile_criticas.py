"""Locust para rutas criticas (no lo ejecuta pytest).

Uso:
    locust -f "Pruebas por modulo/rendimiento/locustfile_criticas.py" \
        --host http://127.0.0.1:5002
"""

from locust import HttpUser, between, task


class UsuarioCritico(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def dashboard(self):
        self.client.get('/dashboard', name='/dashboard')

    @task(2)
    def guiones(self):
        self.client.get('/guiones/', name='/guiones/')

    @task(2)
    def en_vivo(self):
        self.client.get('/en-vivo/', name='/en-vivo/')

    @task(1)
    def balance(self):
        self.client.get('/balance/', name='/balance/')

    @task(1)
    def reportes(self):
        self.client.get('/reportes/', name='/reportes/')

    @task(1)
    def login(self):
        self.client.get('/auth/login', name='/auth/login')
