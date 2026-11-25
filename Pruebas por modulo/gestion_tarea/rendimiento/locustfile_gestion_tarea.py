from locust import HttpUser, between, task


class UsuarioGestionTarea(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/gestion-tarea/', name='/gestion-tarea/')
