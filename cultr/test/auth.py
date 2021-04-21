import random
import string

from . import client


def get_auth_headers(username, password):
    r = client.post("/api/users", data={
        "username": username,
        "password": password
    })

    assert r.status_code in (201, 409)

    r = client.post(
        "/api/token",
        data={"username": username, "password": password}
    )

    assert r.status_code == 201

    return {
        "Authorization": f"Bearer {r.json()['access_token']}"
    }


def random_creds():
    username = ''.join(random.choices(string.ascii_letters, k=10))
    password = ''.join(random.choices(string.ascii_letters, k=10))
    return username, password
