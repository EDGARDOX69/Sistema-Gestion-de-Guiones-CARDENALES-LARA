from locust import HttpUser, between, task


class UsuarioEnVivo(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/en-vivo/', name='/en-vivo/')
