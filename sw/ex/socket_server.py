import socket


def server_program():
    #host = socket.gethostname() # get the hostname
    #host = '127.0.0.1'
    host = '192.168.0.154'
    port = 2005  # initiate port no above 1024
    server_socket = socket.socket()  # instantiate
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))  # bind host address and port together
    server_socket.listen(2) # configure how many client the server can listen simultaneously
    print('Server accepting...')
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))

    while True:
        try:
            data = conn.recv(1024).decode() # receive data stream. accept data packet no greater than 1024 bytes
            if not data: # if data is not received break
                print('No data from client. Socket closed. Exit...')
                break
            print("from connected user: " + str(data))
            message = input(' -> ')
            if message.lower().strip() ==  'close':
                print('Closing server socket')
                conn.close()
                conn == None
                break
            conn.send(message.encode())  # send data to the client
        except Exception as e:
            print(f'Server exceptin: {e}')

    try:
        if conn:
            conn.close()  # close the connection
        server_socket.close()
    except Exception as e:
        print(f'Exception while close server sockets:{e}')

if __name__ == '__main__':
    server_program()
