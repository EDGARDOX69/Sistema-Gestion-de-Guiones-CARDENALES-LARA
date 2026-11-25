from locust import HttpUser, between, task


class UsuarioMantenimiento(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/mantenimiento/', name='/mantenimiento/')
