import socket
import threading
import time


class SocketServer:
    def __init__(self, host='127.0.0.1', port=5000):   
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"서버가 {host}:{port}에서 시작되었습니다.")
        self.client_sockets = []  # 연결된 클라이언트 소켓 리스트
        self.relay_client = None  # 중계 클라이언트 객체

    def handle_connection(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"클라이언트 연결됨: {addr}")
            self.client_sockets.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                print(f"서버에서 받은 데이터: {data}")
                self.forward_to_relay(data)
            except ConnectionResetError:
                print("클라이언트 연결이 종료되었습니다.")
                break
        self.client_sockets.remove(client_socket)
        client_socket.close()

    def forward_to_relay(self, data):
        if not self.relay_client or not self.relay_client.is_connected():
            print("PLC에 연결 중...")
            self.relay_client = SocketClient()
        self.relay_client.send_data(data)

    def broadcast_to_clients(self, data):
        print(f"모든 PC로 데이터 전송: {data}")
        for client_socket in self.client_sockets:
            try:
                client_socket.send(data.encode())
            except (BrokenPipeError, ConnectionResetError):
                self.client_sockets.remove(client_socket)


class SocketClient:
    def __init__(self, host='127.0.0.1', port=6000):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
        self.connect_to_relay()
        threading.Thread(target=self.receive_from_relay).start()

    def connect_to_relay(self):
        while not self.connected:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.host, self.port))
                self.connected = True
                print(f"plc {self.host}:{self.port}에 연결되었습니다.")
            except (ConnectionRefusedError, OSError):
                print(f"plc {self.host}:{self.port}에 연결 실패. 재시도 중...")
                time.sleep(5)  # 5초 후 재시도

    def is_connected(self):
        return self.connected

    def send_data(self, data):
        try:
            self.client_socket.send(data.encode())
            print(f"pc로 데이터 전송: {data}")
        except (BrokenPipeError, ConnectionResetError):
            print("pc와의 연결이 끊어졌습니다. 재연결 시도 중...")
            self.connected = False
            self.connect_to_relay()

    def receive_from_relay(self):
        while True:
            try:
                if self.connected:
                    data = self.client_socket.recv(1024).decode()
                    if data:
                        print(f"plc에서 받은 데이터: {data}")
                        relay_server.broadcast_to_clients(data)
            except (ConnectionResetError, OSError):
                print("plc와의 연결이 끊어졌습니다. 재연결 시도 중...")
                self.connected = False
                self.connect_to_relay()


if __name__ == "__main__":
    relay_server = SocketServer()
    server_thread = threading.Thread(target=relay_server.handle_connection)
    server_thread.daemon = True
    server_thread.start()

    print("서버가  동작 중입니다.")
    server_thread.join()