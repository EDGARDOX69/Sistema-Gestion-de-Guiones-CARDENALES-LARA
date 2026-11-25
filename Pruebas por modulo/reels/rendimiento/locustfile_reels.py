from locust import HttpUser, between, task


class UsuarioReels(HttpUser):
    wait_time = between(1, 2)

    @task
    def principal(self):
        self.client.get('/reels/', name='/reels/')
