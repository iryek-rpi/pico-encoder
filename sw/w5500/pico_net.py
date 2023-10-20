from usocket import socket
import uselect
import uasyncio

from w5500 import w5x00_init

ASYNC_SLEEP_MS = 30

def init_ip(is_dhcp, ip, subnet, gateway):
    if is_dhcp:
        net_info = w5x00_init(None)
    else:
        net_info = w5x00_init((ip, subnet, gateway))

    return net_info

def get_poller(polled, poller=None):
    if not poller:
        poller = uselect.poll()
    poller.register(polled, uselect.POLLIN)
    return poller

def init_server_sockets(ip, port, port2):
    sock = socket()
    sock.bind((ip, int(port)))
    print('Listening on socket: ', sock, 'port:', port)
    sock.listen(2)
    sock_poller = get_poller(sock, None)
    print('sock_poller: ', sock_poller)

    sock2 = socket()
    sock2.bind((ip, int(port2)))
    print('Listening on socket: ', sock2, 'port:', port2)
    sock2.listen(2)
    sock_poller = get_poller(sock2, sock_poller)
    print('sock_poller: ', sock_poller)

    return sock, sock2, sock_poller

async def send_data(data, peer_ip, peer_port):
    sock = socket()
    sock.connect((peer_ip, peer_port))
    print('Sending data: ', data, ' to ', peer_ip, ':', peer_port)
    msg_len = len(data)
    while msg_len>0:
        sent = sock.write(data)
        msg_len -= sent
        data = data[sent:]
        uasyncio.sleep_ms(ASYNC_SLEEP_MS)
    sock.close()

def init_connection(server_sock, poller):
    conn, addr = server_sock.accept()
    print('Connected by ', conn, ' from ', addr)
    sock_data_poller = get_poller(conn, poller)

    return conn, addr, sock_data_poller

def close_sockets(*args):
    for sock in args:
        if sock:
            sock.close()