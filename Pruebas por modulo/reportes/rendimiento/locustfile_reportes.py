from locust import HttpUser, between, task


class UsuarioReportes(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/reportes/', name='/reportes/')
