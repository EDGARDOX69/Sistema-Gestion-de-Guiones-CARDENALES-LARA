from locust import HttpUser, between, task


class UsuarioInventario(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/inventario/', name='/inventario/')
