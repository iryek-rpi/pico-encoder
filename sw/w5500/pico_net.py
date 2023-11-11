from machine import Pin
from machine import SPI
from machine import UART
from usocket import socket
import utime
import uselect
import uasyncio
import utils

ASYNC_SLEEP_MS = 30

def init_serial(baud, parity, bits, stop, timeout):
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    if parity=='N':
        parity = None
    uart0.init(baudrate=baud, bits=bits, parity=parity, stop=stop, timeout=timeout)
    return uart0

def w5x00_init(net_config):
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    
    nic.active(True)
    nic.ifconfig((net_config[0], net_config[1], net_config[2],'8.8.8.8'))

    wait_count = 0
    while not nic.isconnected():
        print(nic.regs())
        print('Waiting for Link...')
        utime.sleep_ms(1000)
        wait_count += 1
        if wait_count > 10:
            return None
    
    ifc = nic.ifconfig()
    print(ifc)
    return ifc

def init_ip(ip, subnet, gateway):
    net_info = w5x00_init((ip, subnet, gateway))
    return net_info

def get_poller(polled, poller=None):
    if not poller:
        poller = uselect.poll()
    poller.register(polled, uselect.POLLIN)
    return poller

def init_server_socket(ip, port, poller):
    sock = socket()
    sock.bind((ip, int(port)))
    print('Listening on socket: ', sock, 'port:', port)
    sock.listen(2)
    sock_poller = get_poller(sock, poller)
    print('sock_poller: ', sock_poller)

    return sock, sock_poller

def close_server_socket(sock, poller):
    sock.close()
    poller.unregister(sock)
    return None

def init_server_sockets(settings, my_ip, text_port, crypto_port):
    poller = uselect.poll()
    serv_sock_crypto, poller = init_server_socket(my_ip, crypto_port, poller)

    serv_sock_text = None
    if settings[utils.CHANNEL] == utils.CH_TCP:
        serv_sock_text, poller = init_server_socket(my_ip, text_port, poller)
    print('serv_sock_text: ', serv_sock_text, 'serv_sock_crypto: ', serv_sock_crypto)
    print('poller: ', poller)

    return serv_sock_text, serv_sock_crypto, poller

def send_data(data, peer_ip, peer_port):
    sock = socket()
    print('Connecting to: ', peer_ip, ':', peer_port)
    print('type(peer_port): ', type(peer_port))
    sock.connect((peer_ip, int(peer_port)))
    print('Sending data: ', data, ' to ', peer_ip, ':', peer_port)
    msg_len = len(data)
    while msg_len>0:
        sent = sock.write(data)
        msg_len -= sent
        data = data[sent:]
        #uasyncio.sleep_ms(ASYNC_SLEEP_MS)
    sock.close()

def send_data_sync(data, peer_ip, peer_port):
    sock = socket()
    print('Connecting to: ', peer_ip, ':', peer_port)
    print('type(peer_port): ', type(peer_port))
    sock.connect((peer_ip, int(peer_port)))
    print('Sending data: ', data, ' to ', peer_ip, ':', peer_port)
    msg_len = len(data)
    while msg_len>0:
        sent = sock.write(data)
        msg_len -= sent
        data = data[sent:]
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