from machine import Pin
from machine import Timer
from machine import UART

from usocket import socket
import utime

import network
import ubinascii

from recv_tcp import w5x00_init

default_led = Pin('LED', Pin.OUT)
default_led_timer = Timer()

print('Starting W5500 script')

def init_serial():    
    uart1 = UART(1, tx=Pin(4), rx=Pin(5))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=10)
    
    return uart1

def main():
    blink_default_led(default_led, default_led_timer)
    u1 = init_serial()
    w5x00_init('192.168.1.10')
    
    sock = socket()
    sock.bind(('192.168.1.10', 5001))
    sock.listen()
    print('listening on socket: ', sock)    

    conn, addr = sock.accept()
    print('Connected by ', conn, 'from ', addr)
    led_on()
    
    while True:
        b64 = conn.recv(256)
        print("data received: ", b64)
        u1.write(b64)


def blink_default_led(led, led_timer):
    global default_led
    global default_led_timer
    
    default_led = led
    default_led_timer = led_timer
    led_timer.init(freq=0.5, mode=Timer.PERIODIC, callback=blink_led)

def blink_led(timer):
    default_led.toggle()

def led_on():
    default_led_timer.deinit()
    default_led.on()

def led_off():
    default_led_timer.deinit()
    default_led.off()


if __name__=='__main__':
    main()