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

default_led = Pin('LED', Pin.OUT)
default_led_timer = Timer()

print('Starting W5500 script')

SERIAL1_TIMEOUT = 20 # ms
UART1_DELAY = 0.05 # 50ms

def init_serial():
    uart1 = UART(1, tx=Pin(4), rx=Pin(5))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)
    
    return uart1

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
    s1 = init_serial()
    json_settings = receive_settings(s1)
    settings = ujson.loads(json_settings)
    print(settings)
    default_led.on()
    print('resetting...')
    utime.sleep(0.5)
    machine.reset()
    

if __name__ == '__main__':
    main()