import socket


def server_program():
    host = socket.gethostname() # get the hostname
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # instantiate
    server_socket.bind((host, port))  # bind host address and port together

    server_socket.listen(2) # configure how many client the server can listen simultaneously
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))

    while True:
        data = conn.recv(1024).decode() # receive data stream. accept data packet no greater than 1024 bytes
        if not data: # if data is not received break
            break
        print("from connected user: " + str(data))
        data = input(' -> ')
        conn.send(data.encode())  # send data to the client

    conn.close()  # close the connection


if __name__ == '__main__':
    server_program()