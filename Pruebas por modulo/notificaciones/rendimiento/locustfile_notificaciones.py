from locust import HttpUser, between, task


class UsuarioNotificaciones(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/notificaciones/api', name='/notificaciones/api')
