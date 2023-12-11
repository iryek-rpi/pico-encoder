import socket
from Cryptodome.Cipher import AES
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Random import get_random_bytes

DEFAULT_LENGTH_KEY = b'aD\xd8\x11e\xdcy`\t\xdc\xe4\xa7\x1f\x11\x94\x93'
DEFAULT_KEY_LEN = len(DEFAULT_LENGTH_KEY)

def fix_len_and_encode_key(key):
    if len(key) > DEFAULT_KEY_LEN:
        key = key[:DEFAULT_KEY_LEN]
    keyb = key.encode()
    return keyb + DEFAULT_LENGTH_KEY[len(keyb):]

def encrypt_text(b64, fixed_binary_key):
    print('OOOOO encrypt text(): data received: ', b64, 'of type(b64): ', type(b64))
    
    #IV = aes.generate_IV(16)
    #cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    IV = AES.get_random_bytes(16)
    cipher = AES.new(fixed_binary_key, AES.MODE_CBC, IV)
    msg = cipher.encrypt(b64)
    print('IV:', IV, ' msg:', msg)
    crypto = IV + msg
    if not crypto:
        print('OOOOO Encryption result Empty')
        crypto = bytes('***BAD DATA***', 'utf-8')
    return crypto

def decrypt_crypto(b64, fixed_binary_key):
    print('XXXXX deecrypt text(): data received: ', b64, 'of type(b64): ', type(b64))

    IV, msg = b64[:16], b64[16:]
    msg = bytearray(msg)
    #cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    cipher = AES.new(fixed_binary_key, AES.MODE_CBC, IV)
    decrypted_msg = cipher.decrypt(msg)
    print('XXXXX decrypted_msg: ', decrypted_msg)
    if not decrypted_msg:
        print('XXXXX Decryption result Empty')
        decrypted_msg = bytes('***BAD DATA***', 'utf-8')
    return decrypted_msg

CRYPTO_IP = '192.168.2.10'
CRYPTO_PORT = 8502
MAX_MSG = 1700

ENC_KEY = '12345678'
DEC_KEY = '12345678'

def main():
    enc_key = fix_len_and_encode_key(ENC_KEY)
    dec_key = fix_len_and_encode_key(DEC_KEY)
    try:
        client = socket.socket()
        client.connect((CRYPTO_IP, CRYPTO_PORT))
        while True:
            msg = input('Enter message: ')
            if msg == '':
                print("Empty message. retry..")
                continue
            client.send(msg.encode())
            response = client.recv(MAX_MSG)
            decrypted = decrypt_crypto(response, dec_key)
            print(f'\n송신: {msg} 수신: {response} 복호결과: {decrypted}')
    except Exception as e:
        print(e)
        return

if __name__ == '__main__':
    main()
