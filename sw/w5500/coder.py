import mpyaes as aes
import led
from main import g_is_xor

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
DEFAULT_KEY_LEN = len(DEFAULT_LENGTH_KEY)

def fix_len_and_encode_key(key):
    if len(key) > DEFAULT_KEY_LEN:
        key = key[:DEFAULT_KEY_LEN]
    keyb = key.encode()
    return keyb + DEFAULT_LENGTH_KEY[len(keyb):]

def encrypt_text(b64, fixed_binary_key):
    print('OOOOO encrypt text(): data received: ', b64, 'of type(b64): ', type(b64))
    
    IV = aes.generate_IV(16)
    cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    msg = cipher.encrypt(b64)
    #print('IV:', IV, ' msg:', msg)
    crypto = IV + msg
    if not crypto:
        led.led_state_data_error()
        print('OOOOO Encryption result Empty')
        crypto = bytes('***BAD DATA***', 'utf-8')
    else:
        led.led_state_good()
    return crypto
    

def decrypt_crypto(b64, fixed_binary_key):
    print('XXXXX deecrypt text(): data received: ', b64, 'of type(b64): ', type(b64))

    IV, msg = b64[:16], b64[16:]
    msg = bytearray(msg)
    cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    decrypted_msg = cipher.decrypt(msg)
    print('XXXXX decrypted_msg: ', decrypted_msg)
    if not decrypted_msg:
        led.led_state_data_error()
        print('XXXXX Decryption result Empty')
        decrypted_msg = bytes('***BAD DATA***', 'utf-8')
    else:
        led.led_state_good()
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