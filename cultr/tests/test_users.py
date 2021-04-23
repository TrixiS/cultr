from . import client
from .auth import random_creds, get_auth_headers


def test_auth():
    username, password = random_creds()

    r = client.post(
        "/api/users",
        data={"username": username, "password": password}
    )

    assert r.status_code == 201

    r = client.post(
        "/api/users",
        data={"username": username, "password": password}
    )

    assert r.status_code == 409
    assert get_auth_headers(username, password)
