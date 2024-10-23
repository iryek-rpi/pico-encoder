from socket import *

host = "192.168.1.30"
port = 5005

ss = socket(AF_INET, SOCK_STREAM)
ss.bind((host,port))
ss.listen(1)
print("listening...")

conso, addr = ss.accept()
print(str(addr), " connected")

data = cs.recv(1024)
print("data received: ", data.decode("utf-8"))

cs.send("from server".encode("utf-8"))
print("message sent")

ss.close()


