import random
import string
import requests as req

from . import url


def get_auth_headers(username, password):
    r = req.post(
        url + "token", data={"username": username, "password": password})

    assert r.status_code == 201

    return {
        "Authorization": f"Bearer {r.json()['access_token']}"
    }


def random_creds():
    username = ''.join(random.choices(string.ascii_letters, k=10))
    password = ''.join(random.choices(string.ascii_letters, k=10))
    return username, password


def test_auth():
    username, password = random_creds()

    r = req.post(
        url + "users", data={"username": username, "password": password})

    assert r.status_code == 201

    r = req.post(
        url + "users", data={"username": username, "password": password})

    assert r.status_code == 409
    return get_auth_headers(username, password)
