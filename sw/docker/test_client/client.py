import socket
import coder

#DEVICE_IP = '192.168.2.10'
DEVICE_IP = '121.190.45.166'
DEVICE_PORT = 2004

MAX_MSG = 1700

KEY = '12345678'

def main():
    fixed_key = coder.fix_len_and_encode_key(KEY)
    try:
        client = socket.socket()
        client.connect((DEVICE_IP, DEVICE_PORT))
        while True:
            msg = input('Enter message: ')
            if msg == '':
                print("Empty message. retry..")
                continue
            client.send(msg.encode())
            response = client.recv(MAX_MSG)
            print(f'\n송신: {msg} 수신: {response}')

            decrypted = coder.decrypt_crypto(response, fixed_key)
            print(f'\n#### 복호결과: {decrypted}')
    except Exception as e:
        print(e)
        return

if __name__ == '__main__':
    main()
