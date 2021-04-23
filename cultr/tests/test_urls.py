from . import client
from .auth import get_auth_headers


class TestUrls:

    url_name = "test"
    url_destination = "https://google.com"
    url_alter_name = "test2"
    url_alter_destination = "https://twitch.tv"
    auth_headers = get_auth_headers("user", "user")

    def test_post(self):
        r = client.post(
            "/api/v1/urls",
            json={"name": self.url_name, "destination": self.url_destination},
            headers=self.auth_headers
        )

        assert r.status_code in (200, 409)

    def test_get_single(self):
        r = client.get(
            "/api/v1/urls/" + self.url_name,
            headers=self.auth_headers
        )

        assert r.status_code == 200
        assert r.json()["name"] == self.url_name

    def test_get_page(self):
        r = client.get("/api/v1/urls", headers=self.auth_headers)
        assert r.status_code == 200
        assert len(r.json()) > 0

    def test_put(self):
        r = client.put(
            f"/api/v1/urls/{self.url_name}",
            json={
                "name": self.url_alter_name,
                "destination": self.url_alter_destination
            },
            headers=self.auth_headers
        )

        assert r.status_code in (204, 409)

    def test_redirect(self):
        r = client.get(f"/u/{self.url_alter_name}")
        assert r.status_code == 307

    def test_delete(self):
        r = client.delete(
            f"/api/v1/urls/{self.url_alter_name}",
            headers=self.auth_headers
        )

        assert r.status_code == 204
