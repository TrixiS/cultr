# %%
import requests as req

# %%
url = "http://127.0.0.1:8000/api/"
j = req.post(url + "token",
             data={"username": "morozov", "password": "rfrdsnfrvj;tnt123"}).json()
h = {
    "Authorization": f"Bearer {j['access_token']}"
}
# %%
r = req.get(url + "v1/urls", headers=h)
print(r.text)
# %%
r = req.post(url + "v1/urls", headers=h, json={
    "name": "some_cool_name",
    "destination": "https://127.0.0.1:8000"
})
