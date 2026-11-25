from locust import HttpUser, between, task


class UsuarioRol(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/roles/', name='/roles/')
