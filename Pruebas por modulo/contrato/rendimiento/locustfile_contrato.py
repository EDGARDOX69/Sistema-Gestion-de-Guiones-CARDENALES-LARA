from locust import HttpUser, between, task


class UsuarioContrato(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/contratos/', name='/contratos/')
