from locust import HttpUser, between, task


class UsuarioGuion(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/guiones/', name='/guiones/')
