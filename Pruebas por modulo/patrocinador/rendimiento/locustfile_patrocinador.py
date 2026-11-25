from locust import HttpUser, between, task


class UsuarioPatrocinador(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/patrocinador/', name='/patrocinador/')
