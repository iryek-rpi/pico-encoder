import socket
import coder

KEY = '12345678'

CRYPTO_SERVER_PORT = 8502
MAX_DATA = 1700

def server_program():
    host = '192.168.2.89'
    port = CRYPTO_SERVER_PORT
    s = socket.socket()
    s.bind((host, port))
    s.listen(2)

    fixed_key = coder.fix_len_and_encode_key(KEY)

    try:
        while True:
            print(f'Server accepting at {host}:{port}...')
            conn, addr= s.accept()
            print("Connection from: " + str(addr))

            while True:
                try:
                    data = conn.recv(MAX_DATA)
                    print(f'#### SERVER: data received: {data}')
                    if not data:
                        print('No data from client. Socket closed. Exit...')
                        conn.close()
                        conn = None
                        break
                    decrypted = coder.decrypt_crypto(data, fixed_key)
                    print(f'\n#### 수신: {data} 복호결과: {decrypted}')

                    encrypted = coder.encrypt_text(decrypted, fixed_key)
                    print(f'#### 암호화 데이터 회신: {encrypted}')
                    conn.send(encrypted) 
                except Exception as e:
                    print(f'Server exceptin: {e}')
    except Exception as e:
        if conn:
            conn.close()
        s.close()

if __name__ == '__main__':
    server_program()