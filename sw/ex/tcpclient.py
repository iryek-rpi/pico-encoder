from socket import *

#ip = "192.168.1.10"
ip = "127.0.0.1"
port = 5002

cs = socket(AF_INET, SOCK_STREAM)
cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
cs.connect((ip, port))

print("connected")
cs.send("123456".encode("utf-8"))
print("123456 send")


data = cs.recv(1024)
print("received: ", data.decode("utf-8"))
cs.close()



