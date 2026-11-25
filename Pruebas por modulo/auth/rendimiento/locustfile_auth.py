from locust import HttpUser, between, task


class UsuarioAuth(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/auth/login', name='/auth/login')
