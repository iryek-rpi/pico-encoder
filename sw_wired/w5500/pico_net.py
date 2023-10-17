from usocket import socket
import uselect

from w5500 import w5x00_init

def pico_net_init(is_dhcp, ip, subnet, gateway):
    if is_dhcp:
        net_info = w5x00_init(None)
    else:
        net_info = w5x00_init((ip, subnet, gateway))

    return net_info

def pico_init_socket(ip, port):
    sock = socket()
    sock.bind((ip, int(port)))
    print('Listening on socket: ', sock)
    sock.listen(2)

    sock_poll = uselect.poll()
    sock_poll.register(sock, uselect.POLLIN)

    print('Waiting for connection...')

    return sock, sock_poll