'''
W5500 
'''
import machine
from machine import Pin
from machine import Timer
from machine import UART

import utime
from usocket import socket
import _thread

import network
import ubinascii
import ujson

from led import *
from w5500 import w5x00_init
import utils

print('Starting W5500 script')
led_onoff(led, False)
led_onoff(yellow, False)
led_onoff(green, False)
led_onoff(red, True)

SERIAL1_TIMEOUT = 300 # ms
UART1_DELAY = 0.05 # 50ms

serial_thread_status = True

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)

    return uart0

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

def serial_thread():
    u0 = init_serial()

    while serial_thread_status:
        sm = u0.readline()
        if sm:
            try:
                sm = sm.decode('utf-8')
                print(sm)
                cmd = sm[:7]
                if cmd=='CNF_REQ':
                    json_settings = utils.load_json_settings()
                    print(f'{len(json_settings)}bytes : {json_settings}')
                    msg = bytes(f'CNF_JSN{json_settings}CNF_END', 'utf-8')
                    u0.write(msg)
                elif cmd=='CONFSND' and sm[-7:]=='CONFEND':
                    json_settings = sm[7:-7]
                    print(json_settings)
                    settings = ujson.loads(json_settings)
                    print(settings)
                else:
                    print('Unknown command')
            except Exception as e:
                print(e)
    u0.deinit()

def send_settings(sp, json_settings):
    len_json = bytes(f'{len(json_settings)}\n', 'utf-8')
    print(len_json)

    while True:
        nw = sp.write(json_settings)
        sp.flush()
        print(f'written: {nw}')
        utime.sleep(1)
        #nw = sp.write(bytes('hello','utf-8'))

        srecv = sp.readline()
        print(srecv)
        if srecv:
            try:
                ready = srecv.decode('utf-8')
                if ready=='READY_0\n':
                    break
            except Exception as e:
                print(e)
        utime.sleep(0.05)
    
def main():
    global serial_thread_status
    
    _thread.start_new_thread(serial_thread, ())

    json_settings = utils.load_json_settings()
    print(json_settings)

    #s0 = init_serial()
    #json_settings = receive_settings(s1)
    #settings = ujson.loads(json_settings)
    #settings['mode'] = 'ETH' #'SER"
    #print(settings)

    #send_settings(s0, json_settings)
    ip = w5x00_init('192.168.2.13')
    if ip:
        print(f'IP assigned: {ip}')
        blue.on()
    else:
        print('No IP assigned')
        led.off()

    serial_thread_status = False
    usleep(3)
    print("Exit from main thread")

temp = '''

    ip = w5x00_init(settings['ip'])

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
                '''

if __name__ == '__main__':
    main()