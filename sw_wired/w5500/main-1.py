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

serial_thread_running = True

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)

    return uart0

def serial_thread_func():
    global serial_thread_running
    u0 = init_serial()

    print('Serial Thread starting...')
    
    while True: #serial_thread_status:
        sm = u0.readline()
        if sm:
            try:
                sm = sm.decode('utf-8')
                sm = sm.strip()
                print(sm)
                cmd = sm[:7]
                print(f'cmd: {cmd}')
                print(f'sm[-7:]: {sm[-7:]}')
                if cmd=='CNF_REQ':
                    json_settings = utils.load_json_settings()
                    print(len(json_settings), ' bytes : ', json_settings)
                    msg = bytes('CNF_JSN', 'utf-8') + bytes(json_settings, 'utf-8') + bytes('CNF_END\n', 'utf-8')
                    u0.write(msg)
                elif cmd=='CNF_WRT' and sm[-7:]=='CNF_END':
                    settings = sm[7:-7]
                    print(f'Received settings: {settings}')
                    utils.save_settings(settings)
                    print('Resetting the machine')
                    machine.reset()
                else:
                    print('Unknown command')
            except Exception as e:
                print(e)
        else:
            print(sm)
            utime.sleep(0.2)
            
    u0.deinit()

def run_server(ip, port)

    server_sock = socket(network.AF_INET, network.SOCK_STREAM)
    server_sock.bind((ip, port))
    
    while True:
        print('Listening on socket: ', server_sock)
        server_sock.listen(3)
        print('Waiting for connection...')
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
    
def main():
    global serial_thread_running
    
    serial_thread_running = True
    
    serial_thread = _thread.start_new_thread(serial_thread_func, ())

    json_settings = utils.load_json_settings()
    print(json_settings)

    if json_settings['dhcp']:
        net_info = w5x00_init(None)
    else:
        net_info = w5x00_init((json_settings['ip'], json_settings['subnet'], json_settings['gateway']))

    if net_info[0]:
        print('IP assigned: ', net_info[0])
        json_settings['ip'] = net_info[0]
        json_settings['subnet'] = net_info[1]
        json_settings['gateway'] = net_info[2]
        utils.save_settings(ujson.dumps(json_settings))
        run_server(json_settings['ip'], json_settings['port'])
        led_onoff(green, True)
        
    else:
        print('No IP assigned')
        led_onoff(yellow, True)

    serial_thread_status = False
    print("Waiting for 15 sec")
    utime.sleep(15)
    
    print("Exit from main thread")

temp = '''
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