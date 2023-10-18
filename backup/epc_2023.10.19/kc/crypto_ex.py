from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

KEY = b'aD\xd8\x11e\xdcy`\t\xdc\xe4\xa7\x1f\x11\x94\x93'
NONCE = b'K\xa2\x02\xb5+N\xd3\x1c\xd9i\xf62\xcf\x95\x93 '
TAG = b'\xf3\xe6\xf34\xd2\xa5K\xe3c\xe3C\xba\x94la\x1b'

#data = b'secret data abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz'

#key = get_random_bytes(16)
#cipher = AES.new(key, AES.MODE_EAX)
#ciphertext, tag = cipher.encrypt_and_digest(data)
#nonce = cipher.nonce

#cipher = AES.new(key, AES.MODE_EAX, nonce)
#data = cipher.decrypt_and_verify(ciphertext, tag)

def enc_aes(key, data):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    nonce = cipher.nonce
    return ciphertext, tag, nonce

def dec_aes(key, ciphertext, tag, nonce):
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data

def main():
    for _ in range(10):
        ciphertext, tag, nonce = enc(KEY, data)
        print(ciphertext, tag, nonce)

        data = dec(KEY, ciphertext, tag, nonce)
        print(data)
        print()