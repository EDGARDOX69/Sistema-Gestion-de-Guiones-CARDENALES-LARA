from locust import HttpUser, between, task


class UsuarioBitacora(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/bitacora/', name='/bitacora/')
