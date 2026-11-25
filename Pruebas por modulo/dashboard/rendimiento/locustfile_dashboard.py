from locust import HttpUser, between, task


class UsuarioDashboard(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/dashboard', name='/dashboard')
