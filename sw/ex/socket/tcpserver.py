import socket

host = "192.168.2.88"
port = 2004

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ss.bind((host,port))
ss.listen(1)
print("listening...")

conn, addr = ss.accept()
print(str(addr), " connected")

data = conn.recv(1024)
print(f"data received: data: {data}", )

print("\nReturning the same data to client")
#conn.send("from server".encode("utf-8"))
conn.send(data)
print("message sent")

conn.close()
ss.close()

