from locust import HttpUser, between, task


class UsuarioPremio(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/premio/', name='/premio/')
