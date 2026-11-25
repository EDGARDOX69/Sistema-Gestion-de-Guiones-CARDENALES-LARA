from locust import HttpUser, between, task


class UsuarioUsuario(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/usuarios/', name='/usuarios/')
