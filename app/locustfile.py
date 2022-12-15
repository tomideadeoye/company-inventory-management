import random
from locust import HttpUser, TaskSet, task, between


class UserLoadTest(HttpUser):
    wait_time = between(5, 9)

    @task
    def users_api(self):
        self.client.get("/api/v1/auth/users/user-list/")


class UserTasks(TaskSet):
    wait_time = between(5, 9)

    @task
    def users_api(self):
        self.client.get("/api/v1/auth/users/user-list/")
