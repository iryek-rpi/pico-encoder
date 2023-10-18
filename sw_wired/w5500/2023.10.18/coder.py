import mpyaes as aes

KEY = b'aD\xd8\x11e\xdcy`\t\xdc\xe4\xa7\x1f\x11\x94\x93'
#NONCE = b'K\xa2\x02\xb5+N\xd3\x1c\xd9i\xf62\xcf\x95\x93 '
#TAG = b'\xf3\xe6\xf34\xd2\xa5K\xe3c\xe3C\xba\x94la\x1b'

#data = b'secret data abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz'

#key = get_random_bytes(16)
#cipher = AES.new(key, AES.MODE_EAX)
#ciphertext, tag = cipher.encrypt_and_digest(data)
#nonce = cipher.nonce

#cipher = AES.new(key, AES.MODE_EAX, nonce)
#data = cipher.decrypt_and_verify(ciphertext, tag)

def enc_aes(key, iv, data):
    cipher = aes.new(key, aes.MODE_CBC, iv)
    ciphertext = data.copy()
    cipher.encrypt(ciphertext)
    return ciphertext

def dec_aes(key, ciphertext, iv):
    cipher = aes.new(key, aes.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

def main():
    for _ in range(10):
        iv = aes.generate_IV(16)
        ciphertext = enc_aes(KEY, iv, data)
        print(ciphertext, iv)

        plaintext = dec_aes(KEY, ciphertext, iv)
        print(plaintext)
        print()