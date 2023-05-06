from socket import *

ip = "192.168.1.10"
port = 5002

cs = socket(AF_INET, SOCK_STREAM)
cs.connect((ip, port))

print("connected")
cs.send("123456".encode("utf-8"))
print("123456 send")


data = cs.recv(1024)
print("received: ", data.decode("utf-8"))
cs.close()



