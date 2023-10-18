from usocket import socket
import uselect

from w5500 import w5x00_init

def pico_net_init(is_dhcp, ip, subnet, gateway):
    if is_dhcp:
        net_info = w5x00_init(None)
    else:
        net_info = w5x00_init((ip, subnet, gateway))

    return net_info

def get_poller(polled):
    poller = uselect.poll()
    poller.register(polled, uselect.POLLIN)
    return poller

def pico_init_socket(ip, port):
    sock = socket()
    sock.bind((ip, int(port)))
    print('Listening on socket: ', sock)
    sock.listen(2)

    sock_poll = get_poller(sock)
    print('Waiting for connection...')

    return sock, sock_poll

def pico_init_conn(server_sock):
    conn, addr = server_sock.accept()
    print('Connected by ', conn, ' from ', addr)
    sock_data_poll = get_poller(conn)

    return conn, addr, sock_data_poll