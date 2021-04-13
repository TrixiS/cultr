# %%
import requests as req
# %%
url = "http://127.0.0.1:8000/api/"
token = req.post(
    url + "token", data={"username": "morozov", "password": "rfrdsnfrvj;tnt123"}).json()["access_token"]
h = {
    "Authorization": f"Bearer {token}"
}

# %%
r = req.get(url + "v1/urls", headers=h)
print(r.text)

# %%
r = req.put(url + "v1/urls" + "/check", headers=h, json={
    "name": "haha",
    "destination": "https://google.com"
})

print(r.status_code)
print(r.text)

# %%
r = req.post(url + "v1/urls", headers=h, json={
    "name": "haha2",
    "destination": "https://google.com"
})

print(r.status_code)
print(r.text)

# %%
