from socket import *
import xor

MSG = "123456"
KEY = 'abcde'

token = xor.create_token(KEY)
bmsg = bytes(MSG, 'utf-8')
print(f'bytes({MSG}: {bmsg}')
encrypted = xor.xor_bin_with_token(bmsg, token)
print(f'Key:{KEY} token:{token} encrypted:{encrypted}') 


ip = "192.168.2.15"
port = 2004

cs = socket(AF_INET, SOCK_STREAM)
cs.connect((ip, port))

print("connected")
#cs.send("123456".encode("utf-8"))
cs.send(encrypted)
print(f"encrypted sent: {encrypted}")


data = cs.recv(1024)
print(f"received: data: {data}")
cs.close()



