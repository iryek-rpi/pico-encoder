'''
W5500 
'''
import machine
from machine import Pin
from machine import Timer
from machine import UART

import utime
from usocket import socket
import uselect
import _thread
import gc

import network
import ubinascii
import ujson
import mpyaes as aes
import usocket

import coder
from led import *
import utils
import pico_net as pn

KEY = b'aD\xd8\x11e\xdcy`\t\xdc\xe4\xa7\x1f\x11\x94\x93'

BAUD_RATE = 9600  #19200
if BAUD_RATE == 9600:
    SERIAL1_TIMEOUT = 200 # ms
else:
    SERIAL1_TIMEOUT = 100 # ms

print('Starting W5500 script')
led_init()
btn = Pin(9, Pin.IN, Pin.PULL_UP)
serial_thread_running = False

def btn_callback(btn):
    global serial_thread_running
    led_onoff(yellow, True)
    led_onoff(green, False)
    print('Button pressed')
    serial_thread_running = False

btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_callback)

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=BAUD_RATE, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)

    return uart0

def do_serial(uart):
    global serial_thread_running
    sm = uart.readline()
    if sm:
        try:
            sm = sm.decode('utf-8')
            sm = sm.strip()
            print(sm)
            cmd = sm[:7]
            print(f'cmd: {cmd}')
            print(f'sm[-7:]: {sm[-7:]}')
            if cmd=='CNF_REQ':
                saved_settings = utils.load_json_settings()
                print('saved_settings: ', saved_settings)
                print('type(saved_settings): ', type(saved_settings))
                str_settings = ujson.dumps(saved_settings)
                print(len(str_settings), ' bytes : ', str_settings)
                msg = bytes('CNF_JSN', 'utf-8') + bytes(str_settings, 'utf-8') + bytes('CNF_END\n', 'utf-8')
                uart.write(msg)
            elif cmd=='CNF_WRT' and sm[-7:]=='CNF_END':
                uart.deinit()
                uart = None
                received_settings = sm[7:-7]
                print(f'Received settings: {received_settings}')
                utils.save_settings(received_settings)
                serial_thread_running = False
                return
            else:
                print('Unknown command')
        except Exception as e:
            print(e)
        
    return

def run_hybrid_server(ip, port, key, uart):
    global serial_thread_running  # reset button flag

    server_sock = socket()
    server_sock.bind((ip, int(port)))
    print('Listening on socket: ', server_sock)
    server_sock.listen(4)

    keyb = coder.fix_len_and_encode_key(key)

    p1 = uselect.poll()
    p1.register(server_sock, uselect.POLLIN)

    print('Waiting for connection...')
    conn = None

    time_start = utime.ticks_ms()

    while serial_thread_running:
        res = p1.poll(100)
        if not res:
            do_serial(uart)
            print('.', end='')
            time_now = utime.ticks_ms()
            runtime = utime.ticks_diff(time_now, time_start)
            if runtime > 25000:
                print(runtime)
                gc.collect()
                time_start = time_now
            continue
        print('client available')
        conn, addr = server_sock.accept()
        print('Connected by ', conn, ' from ', addr)
        break

    if not serial_thread_running:
        if conn:
            conn.close()
        server_sock.close()
        return
        
    poller = uselect.poll()
    poller.register(conn, uselect.POLLIN)
    
    time_start = utime.ticks_ms()

    while serial_thread_running:
        res = poller.poll(100)
        if not res:
            do_serial(uart)
            print('no data from conn')
            time_now = utime.ticks_ms()
            runtime = utime.ticks_diff(time_now, time_start)
            if runtime > 25000:
                print(runtime)
                gc.collect()
                time_start = time_now
            continue

        print('data arrived at conn')

        b64 = conn.recv(128)
        print('data received: ', b64)
        print('type(b64): ', type(b64))
        
        if len(b64) <= 4:
            print('irregular data. Exit')
            break
        else:
            cmd, msg = b64[:4], b64[4:]
            cmd = cmd.decode('utf-8')
            print(f'cmd: {cmd}')

            if cmd == 'TEXT':
                print(f'msg: {msg}')
                IV = aes.generate_IV(16)
                cipher = aes.new(keyb, aes.MODE_CBC, IV)
                msg = cipher.encrypt(msg)
                iv_c = IV + msg
                print('IV: ')
                print(IV)
                print('msg: ')
                print(msg)
                conn.send(iv_c)
            elif cmd == 'CIPH':
                print(f'msg: {msg}')
                IV, msg = msg[:16], msg[16:]
                print('IV: ')
                print(IV)
                print('msg: ')
                print(msg)
                msga = bytearray(msg)
                cipher = aes.new(keyb, aes.MODE_CBC, IV)
                plaintext = cipher.decrypt(msga)
                conn.send(plaintext)

    if conn:
        conn.close()
    if server_sock:
        server_sock.close()
    if uart:
        uart.deinit()

    utime.sleep(2)

    #machine.reset()
    return

def run_server_serial(uart):
    global serial_thread_running  # reset button flag

    time_start = utime.ticks_ms()

    while serial_thread_running:
        do_serial(uart)
        print('.', end='')
        time_now = utime.ticks_ms()
        runtime = utime.ticks_diff(time_now, time_start)
        if runtime > 25000:
            print(runtime)
            gc.collect()
            time_start = time_now
        continue

    if uart:
        uart.deinit()

    utime.sleep(2)

    return

def main_single():
    global serial_thread_running

    led_start()
    settings = utils.load_json_settings()
    print(settings)

    serial_thread_running = True
    uart = init_serial()
    net_info = pn.pico_net_init(settings['dhcp'], settings['ip'], settings['subnet'], settings['gateway'])

    if net_info and net_info[0]:
        led_state_good()
        print('IP assigned: ', net_info[0])
        settings['ip'], settings['subnet'], settings['gateway'] = net_info[0], net_info[1], net_info[2]
        utils.save_settings(ujson.dumps(settings))
        run_hybrid_server(settings['ip'], settings['port'], settings['key'], uart)
    else:
        print('No IP assigned')
        led_state_no_ip()
        run_serial_server(uart)

    led_onoff(green, False)
    print("Waiting for 2 sec")
    utime.sleep(2)
    print("Exit from main function")

    machine.reset()

if __name__ == '__main__':
    main_single()