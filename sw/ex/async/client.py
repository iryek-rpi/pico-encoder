import sys
import time
import logging
import socket

c_socket = None

def init_connection(ip, port):
    global c_socket

    try:
        if c_socket:
            c_socket.close()
            c_socket = None
        c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_socket.connect((ip, port))
    except socket.error:
        if c_socket:
            c_socket.close()
            c_socket = None
        return None
    except ValueError:
        if c_socket:
            c_socket.close()
            c_socket = None
        return None
    else:
        return c_socket

IP = 'localhost'
PORT = 8000

def main():
    global c_socket

    c_socket = init_connection(IP, PORT)

    if not c_socket:
        print(f'Failed to connect to server at {IP}:{PORT}')
        return

    msg = None
    while True:
        if c_socket and msg:
            c_socket.send(msg.encode())

            iv_c = c_socket.recv(64)
            if iv_c == b'':
                print('Server closed connection')
                c_socket.close()
                c_socket = None
                break

            print(f'IV received from server: {iv_c.decode()}')

        msg = input('Enter message to send: ') + '\n'

if __name__ == '__main__':
    main()