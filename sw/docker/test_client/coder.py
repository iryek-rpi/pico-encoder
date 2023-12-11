from Cryptodome.Cipher import AES
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Util.Padding import unpad
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
    if type(b64) == str:
        b64 = b64.encode('utf-8')
    
    #IV = aes.generate_IV(16)
    #cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    IV = AES.get_random_bytes(16)
    cipher = AES.new(fixed_binary_key, AES.MODE_CBC, IV)
    msg = cipher.encrypt(pad(b64, AES.block_size))
    #msg = cipher.encrypt(b64)
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
    decrypted_msg = unpad(decrypted_msg, AES.block_size)
    print('XXXXX decrypted_msg: ', decrypted_msg)
    if not decrypted_msg:
        print('XXXXX Decryption result Empty')
        decrypted_msg = bytes('***BAD DATA***', 'utf-8')

    decrypted_msg = decrypted_msg.decode('utf-8').strip()
    return decrypted_msg
