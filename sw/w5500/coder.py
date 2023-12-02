import mpyaes as aes
import net_utils as nu

#NONCE = b'K\xa2\x02\xb5+N\xd3\x1c\xd9i\xf62\xcf\x95\x93 '
#TAG = b'\xf3\xe6\xf34\xd2\xa5K\xe3c\xe3C\xba\x94la\x1b'

#data = b'secret data abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz'

#key = get_random_bytes(16)
#cipher = AES.new(key, AES.MODE_EAX)
#ciphertext, tag = cipher.encrypt_and_digest(data)
#nonce = cipher.nonce

#cipher = AES.new(key, AES.MODE_EAX, nonce)
#data = cipher.decrypt_and_verify(ciphertext, tag)
import mpyaes as aes
DEFAULT_LENGTH_KEY = b'aD\xd8\x11e\xdcy`\t\xdc\xe4\xa7\x1f\x11\x94\x93'
default_key_len = len(DEFAULT_LENGTH_KEY)

def fix_len_and_encode_key(key):
    if len(key) > default_key_len:
        key = key[:default_key_len]
    keyb = key.encode()
    return keyb + DEFAULT_LENGTH_KEY[len(keyb):]

def encrypt_text(b64, fixed_binary_key, dest):
    print('data received: ', b64, 'of type(b64): ', type(b64))
    
    IV = aes.generate_IV(16)
    print('fixed_binary_key: ', fixed_binary_key, 'type(fixed_binary_key): ', type(fixed_binary_key))
    cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    msg = cipher.encrypt(b64)
    print('IV:', IV, ' msg:', msg)
    encrypted_msg = IV + msg

    print(f'dest: {dest}')
    dest[1](encrypted_msg, dest[0])
    return encrypted_msg


def decrypt_crypto(b64, fixed_binary_key, dest):
    print('data received: ', b64)
    print('type(b64): ', type(b64))
    
    print('b64: ', b64)
    IV, msg = b64[:16], b64[16:]
    print('IV:', IV, ' msg:', msg)
    msg_ba = bytearray(msg)
    cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    decrypted_msg = cipher.decrypt(msg_ba)
    print('decrypted_msg: ', decrypted_msg)

    dest[1](decrypted_msg, dest[0])
    return decrypted_msg

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
        ciphertext = enc_aes(DEFAULT_LENGTH_KEY, iv, data)
        print(ciphertext, iv)

        plaintext = dec_aes(DEFAULT_LENGTH_KEY, ciphertext, iv)
        print(plaintext)
        print()