from machine import Pin
from machine import SPI
from machine import UART
from usocket import socket
import utime
import ujson as json
import uselect
import uasyncio
import network
from led import *
import constants as c
import utils

SERIAL1_TIMEOUT = 50 # ms
ASYNC_SLEEP_MS = 30
SERIAL_BUF = 1024

def init_serial(baud, parity, bits, stop, timeout):
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    parity = None if parity=='N' else int(parity)
    uart0.init(int(baud), int(bits), parity, int(stop), timeout=timeout, txbuf=SERIAL_BUF, rxbuf=SERIAL_BUF)
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

def init_connections(settings):
    uart = init_serial(settings[utils.SPEED], settings[utils.PARITY], settings[utils.DATA], settings[utils.STOP], SERIAL1_TIMEOUT)
    net_info = w5x00_init((settings['ip'], settings['subnet'], settings['gateway']))

    if net_info and net_info[0]:
        led_state_good()
        print('IP assigned: ', net_info[0])
        settings['ip'], settings['subnet'], settings['gateway'] = net_info[0], net_info[1], net_info[2]
        utils.save_settings(settings)
    else:
        led_state_no_ip()
        settings['ip'] = None
        print('No IP assigned')
    
    return uart, settings

def get_poller(polled, poller=None):
    if not poller:
        poller = uselect.poll()
    poller.register(polled, uselect.POLLIN)
    return poller

def init_serv_socket(ip, port):
    sock = socket()
    sock.bind((ip, int(port)))
    print('Listening on socket: ', sock, 'port:', port)
    sock.listen(2)
    return sock


def init_server_socket(ip, port):
    sock = socket()
    sock.bind((ip, int(port)))
    print('Listening on socket: ', sock, 'port:', port)
    sock.listen(2)
    poller = uselect.poll()
    sock_poller = get_poller(sock, poller)
    print('sock_poller: ', sock_poller)

    return sock, sock_poller

def init_server_socket_async(ip, port, poller):
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

def init_server_sockets_async(settings, my_ip, text_port, crypto_port):
    poller = uselect.poll()
    serv_sock_crypto, poller = init_server_socket_async(my_ip, crypto_port, poller)

    serv_sock_text = None
    if settings[utils.CHANNEL] == c.CH_TCP:
        serv_sock_text, poller = init_server_socket_async(my_ip, text_port, poller)
    print('serv_sock_text: ', serv_sock_text, 'serv_sock_crypto: ', serv_sock_crypto)
    print('poller: ', poller)

    return serv_sock_text, serv_sock_crypto, poller

def init_server_sockets(settings, my_ip, text_port, crypto_port):
    serv_sock_crypto, serv_sock_crypto_poller = init_server_socket(my_ip, crypto_port)

    serv_sock_text = None
    serv_sock_text_poller = None
    if settings[utils.CHANNEL] == c.CH_TCP:
        serv_sock_text, serv_sock_text_poller = init_server_socket(my_ip, text_port)
    print('serv_sock_text: ', serv_sock_text, 'serv_sock_crypto: ', serv_sock_crypto)
    print('crypto_poller: ', serv_sock_crypto_poller)
    print('text_poller: ', serv_sock_text_poller)

    return serv_sock_text, serv_sock_crypto, serv_sock_text_poller, serv_sock_crypto_poller

def init_connection(server_sock, poller):
    conn, addr = server_sock.accept()
    print('Connected by ', conn, ' from ', addr)
    if not poller:
        poller = uselect.poll() 
        poller = get_poller(conn, poller)

    return conn, addr, poller

def close_sockets(*args):
    for sock in args:
        if sock:
            sock.close()