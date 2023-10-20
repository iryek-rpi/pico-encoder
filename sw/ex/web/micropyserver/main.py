from micropyserver import MicroPyServer
from usocket import socket
import uselect

from w5500 import w5x00_init

server = None

def init_ip(is_dhcp, ip, subnet, gateway):
    if is_dhcp:
        net_info = w5x00_init(None)
    else:
        net_info = w5x00_init((ip, subnet, gateway))

    return net_info

def hello_world(request):
    server.send("Hello World!")

def main():
    global server

    net_info = init_ip(True, None, None, None)
    print(net_info)
    server = MicroPyServer()
    server.add_route("/", hello_world)
    server.start()

if __name__ == "__main__":
    main()

