'''
W5500 
'''
from machine import Pin
from machine import Timer
from machine import UART

import utime
from usocket import socket

import network
import ubinascii
import ujson

default_led = Pin('LED', Pin.OUT)
default_led_timer = Timer()

print('Starting W5500 script')

SERIAL1_TIMEOUT = 500

def init_serial():
    uart1 = UART(1, tx=Pin(4), rx=Pin(5))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)
    
    return uart1

def main():
    s1 = init_serial()
    default_led.on()
    
    s1.write(bytes('READY','utf-8'))
    len_json = b''
    rc = s1.read(1)
    print(rc)
    while True:
        if rc:
            if rc.decode('utf-8') == '\n':
                break
        if rc and rc !=b'\x00':
            len_json += rc
        rc = s1.read(1)
        print(rc)
    
    print(f'len_json: {len_json}')
    len_json = len_json.decode('utf-8')
    print(f'len_json: {len_json}')
    
    s1.write(bytes('READY','utf-8'))
    
    json_data = s1.read(int(len_json))
    print(f'json_data: {json_data}')
    json_data = json_data.decode('utf-8')
    data = ujson.loads(json_data)
    print(f'data: {data}')

if __name__ == '__main__':
    main()