from socket import *

#host = "192.168.1.30"
host = "127.0.0.1"
port = 5005

ss = socket(AF_INET, SOCK_STREAM)
ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ss.bind((host,port))
ss.listen(1)
print("listening...")

conso, addr = ss.accept()
print(str(addr), " connected")

data = conso.recv(1024)
print("data received: ", data.decode("utf-8"))

conso.send("from server".encode("utf-8"))
print("message sent")

conso.close()


