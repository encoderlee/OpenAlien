import random
import hashlib
from dataclasses import dataclass
import time
from binascii import hexlify

@dataclass()
class Nonce:
    random_string: str
    hex_digest: str


def random_bytes(count: int):
    return bytes([random.getrandbits(8) for i in range(0, count)])


def str_to_hex(c):
    hex_data = hexlify(bytearray(c, 'ascii')).decode()
    return int(hex_data, 16)


def char_subtraction(a, b, add):
    x = str_to_hex(a)
    y = str_to_hex(b)
    ans = str((x - y) + add)
    if len(ans) % 2 == 1:
        ans = '0' + ans
    return int(ans)

def char_to_symbol(c):
    if 'a' <= c <= 'z':
        return char_subtraction(c, 'a', 6)
    if '1' <= c <= '5':
        return char_subtraction(c, '1', 1)
    return 0

def string_to_name(s):
    i = 0
    name = 0
    while i < len(s):
        name += (char_to_symbol(s[i]) & 0x1F) << (64 - 5 * (i + 1))
        i += 1
    if i > 12:
        name |= char_to_symbol(s[11]) & 0x0F
    return name


def generate_nonce(account_name: str, last_mine_trx: str, difficulty=0) -> Nonce:
    account_arr = string_to_name(account_name).to_bytes(8, "little")
    last_mine_arr = bytes.fromhex(last_mine_trx)[:8]
    zeroes = 4 if account_name[-4:] == ".wam" else 6
    while True:
        random_arr = random_bytes(8)
        temp_arr = bytearray(account_arr + last_mine_arr + random_arr)
        hash256 = hashlib.sha256(temp_arr).hexdigest()
        if hash256[:zeroes] != "0" * zeroes:
            continue
        if int(hash256[zeroes: zeroes+1], 16) <= difficulty:
            break
    return Nonce(random_arr.hex(), hash256)


def test():
    account_name = "m45yy.wam"
    last_mine_trx = "41aaf836170e3a72994d658707162f825bf5e27ed786e4f76acaad844ce5da09"
    t1 = time.time()
    ret = generate_nonce(account_name, last_mine_trx)
    print(ret)
    print(time.time() - t1)


if __name__ == '__main__':
    test()
