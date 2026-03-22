import os
from uuid import uuid4

from locust import HttpUser, between, task


PASSWORD = os.getenv("LOCUST_TEST_PASSWORD", "password123")


def make_email() -> str:
    return f"locust-{uuid4().hex}@test.com"


def make_url() -> str:
    return f"https://example.com/{uuid4().hex}"


class PublicLinksUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:
        self.short_code: str | None = None
        self.original_url: str | None = None

    @task(3)
    def create_public_link(self) -> None:
        original_url = make_url()
        with self.client.post(
            "/links/shorten",
            json={"url": original_url},
            name="/links/shorten [public]",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return

            payload = response.json()
            self.short_code = payload["short_code"]
            self.original_url = payload["url"]
            response.success()

    @task(2)
    def redirect_by_short_code(self) -> None:
        if not self.short_code:
            self.create_public_link()
        if not self.short_code:
            return

        with self.client.get(
            f"/links/{self.short_code}",
            name="/links/{short_code}",
            allow_redirects=False,
            catch_response=True,
        ) as response:
            if response.status_code != 302:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return

            location = response.headers.get("location")
            if self.original_url and location != self.original_url:
                response.failure(f"unexpected redirect location: {location}")
                return
            response.success()

    @task(1)
    def get_stats(self) -> None:
        if not self.short_code:
            self.create_public_link()
        if not self.short_code:
            return

        with self.client.get(
            f"/links/{self.short_code}/stats",
            name="/links/{short_code}/stats",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return
            response.success()

    @task(1)
    def search_by_original_url(self) -> None:
        if not self.original_url:
            self.create_public_link()
        if not self.original_url:
            return

        with self.client.get(
            "/links/search",
            params={"original_url": self.original_url},
            name="/links/search",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return
            response.success()


class AuthenticatedLinksUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:
        self.email = make_email()
        self.headers: dict[str, str] = {}
        self.short_code: str | None = None
        self.original_url: str | None = None

        self.register()
        self.login()

    def register(self) -> None:
        with self.client.post(
            "/auth/register",
            json={"email": self.email, "password": PASSWORD},
            name="/auth/register",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return
            response.success()

    def login(self) -> None:
        with self.client.post(
            "/auth/jwt/login",
            data={"username": self.email, "password": PASSWORD},
            name="/auth/jwt/login",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return

            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
            response.success()

    @task(3)
    def create_owned_link(self) -> None:
        original_url = make_url()
        with self.client.post(
            "/links/shorten",
            json={"url": original_url},
            headers=self.headers,
            name="/links/shorten [auth]",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return

            payload = response.json()
            self.short_code = payload["short_code"]
            self.original_url = payload["url"]
            response.success()

    @task(2)
    def list_my_links(self) -> None:
        with self.client.get(
            "/links/my",
            headers=self.headers,
            name="/links/my",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return
            response.success()

    @task(1)
    def update_owned_link(self) -> None:
        if not self.short_code:
            self.create_owned_link()
        if not self.short_code:
            return

        new_alias = f"alias{uuid4().hex[:8]}"
        new_url = make_url()
        with self.client.put(
            f"/links/{self.short_code}",
            json={"url": new_url, "alias": new_alias},
            headers=self.headers,
            name="/links/{short_code} [PUT]",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return

            payload = response.json()
            self.short_code = payload["short_code"]
            self.original_url = payload["url"]
            response.success()

    @task(1)
    def delete_owned_link(self) -> None:
        if not self.short_code:
            self.create_owned_link()
        if not self.short_code:
            return

        with self.client.delete(
            f"/links/{self.short_code}",
            headers=self.headers,
            name="/links/{short_code} [DELETE]",
            catch_response=True,
        ) as response:
            if response.status_code != 204:
                response.failure(
                    f"unexpected status: {response.status_code} {response.text}")
                return

            self.short_code = None
            self.original_url = None
            response.success()
