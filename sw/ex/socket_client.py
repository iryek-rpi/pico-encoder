import socket
import time

def connect_to_server(client_socket, server_ip, server_port):
    while True:
        try:
            print('client connecting...')
            time.sleep(1)
            client_socket.connect((server_ip, server_port))
            print('client connected: ')
            break
        except Exception as e:
            print(f'Exception:{e}')

def client_program():
    #host = socket.gethostname()  # as both code is running on same pc
    host = '127.0.0.1'
    port = 5005  # socket server port number
    client_socket = socket.socket()  # instantiate
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #client_socket.connect((host, port))  # connect to the server
    print(f'Client connecting to server: {host}:{port}')
    connect_to_server(client_socket, host, port)

    message = input(" -> ")  # take input

    while message.lower().strip() != 'bye':
        try:
            client_socket.send(message.encode())  # send message
            print('Client receving...')
            data = client_socket.recv(1024).decode()  # receive response
            if not data: # if data is not received break
                print('No data from server. Socket closed. Exit...')
                break

            print('Received from server: ' + data)  # show in terminal

            message = input(" -> ")  # again take input
            if message.lower().strip() ==  'close':
                print('Closing client socket')
                client_socket.close()
                client_socket == None
                break
        except Exception as e:
            print(f'Client exceptin: {e}')

    if client_socket:
        client_socket.close()  # close the connection

if __name__ == '__main__':
    client_program()