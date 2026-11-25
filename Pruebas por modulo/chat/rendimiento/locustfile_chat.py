from locust import HttpUser, between, task


class UsuarioChat(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/asistente/', name='/asistente/')
