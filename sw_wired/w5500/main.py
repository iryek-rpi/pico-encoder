'''
W5500 
'''
import machine
from machine import Pin
from machine import Timer
from machine import UART

import utime
from usocket import socket

import network
import ubinascii
import ujson

from w5500 import w5x00_init

default_led = Pin('LED', Pin.OUT)
default_led_timer = Timer()
red_led = Pin(14, Pin.OUT)
red_led.on()
green_led = Pin(15, Pin.OUT)
green_led.on()

print('Starting W5500 script')

SERIAL1_TIMEOUT = 20 # ms
UART1_DELAY = 0.05 # 50ms
SIG = '*x?!926'

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)

    uart1 = UART(1, tx=Pin(4), rx=Pin(5))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)
    
    return uart0, uart1

def receive_settings(sp):
    while True:
        sp.write(bytes('READY_1\n', 'utf-8'))
        utime.sleep(UART1_DELAY*2)
        srecv = sp.readline()
        print(srecv)
        try:
            len_settings = int(srecv.decode('utf-8').strip())
            break
        except Exception as e:
            print(e)

    print(f'len_settings:{len_settings}')

    while True:
        sp.write(bytes('READY_2\n', 'utf-8'))
        utime.sleep(UART1_DELAY*2)
        srecv = sp.read(len_settings)
        print(srecv)
        try:
            json_settings = srecv.decode('utf-8')
            break
        except Exception as e:
            print(e)

    print(json_settings)
    return json_settings

def main():
    s0, s1 = init_serial()
    json_settings = receive_settings(s1)
    settings = ujson.loads(json_settings)
    #settings['mode'] = 'ETH' #'SER"
    print(settings)

    ip = w5x00_init(settings['ip'])
    default_led.on()

    server_sock = socket() #network.AF_INET, network.SOCK_STREAM)
    server_sock.bind((ip, settings['port']))

    #client_sock = socket(network.AF_INET, network.SOCK_STREAM)
    red_led.off()
    
    if settings['mode'] == 'ETH':
        while True:
            server_sock.listen()
            print('Listening on socket: ', server_sock)

            conn, addr = server_sock.accept()
            print('Connected by ', conn, ' from ', addr)
            b64 = conn.recv(32)
            print('data received: ', b64)
            print('type(b64): ', type(b64))
            if addr != settings['remote_ip']:
                print('Not from remote')
                remote_sock = socket()
                print(f"connecting to remote {settings['remote_ip']}:{settings['remote_port']}")
                #remote_sock.connect((settings['remote_ip'], settings['remote_port']))
                remote_sock.connect(('192.168.0.254', 2004))
                print(f"send {b64} to remote")
                remote_sock.send(b64)
                client_sock = conn
                client_addr = addr
                print("waiting for response from remote")
                b64 = remote_sock.recv(32)
                print(f"received {b64} from remote")
                remote_sock.close()
                client_sock.send(b64)
                print(f"sent {b64} to client")
                client_sock.close()
            else:
                print('From remote')
                remote_sock = conn
                remote_addr = addr
                plc_sock = socket()
                print(f"connecting to plc {settings['plc_ip']}:{settings['plc_port']}")
                plc_sock.connect((settings['plc_ip'], settings['plc_port']))
                print(f"send {b64} to plc")
                plc_sock.send(b64)
                print("waiting for response from plc")
                b64 = plc_sock.recv(32)
                print(f"received {b64} from plc")
                plc_sock.close()
                remote_sock.send(b64)
                print(f"sent {b64} to remote")
                remote_sock.close()
    else:
        while True:
            server_sock.listen()
            print('Listening on socket: ', server_sock)

            conn, addr = server_sock.accept()
            print('Connected by ', conn, ' from ', addr)
            b64 = conn.recv(32)
            print('data received: ', b64)
            print('type(b64): ', type(b64))
            if addr != settings['remote_ip']:
                print('Not from remote')
                remote_sock = socket()
                print(f'connecting to remote {settings['remote_ip']}:{settings['remote_port']}')
                remote_sock.connect((settings['remote_ip'], settings['remote_port']))
                remote_sock.send(b64)
                client_sock = conn
                client_addr = addr
                b64 = remote_sock.recv(32)
                remote_sock.close()
                client_sock.send(b64)
                client_sock.close()
            else:
                print('From remote')
                remote_sock = conn
                remote_addr = addr
                server_sock = socket()
                print(f'connecting to server {settings['server_ip']}:{settings['server_port']}')
                server_sock.connect((settings['server_ip'], settings['server_port']))
                server_sock.send(b64)
                b64 = server_sock.recv(32)
                server_sock.close()
                remote_sock.send(b64)
                remote_sock.close()
    

if __name__ == '__main__':
    main()