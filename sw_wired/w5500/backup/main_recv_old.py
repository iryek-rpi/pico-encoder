from machine import Pin
from machine import Timer
from machine import UART
from usocket import socket
import network
import ubinascii

import time

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
        b64 = conn.recv(5)
        print("data received: ", b64)
        led_on()
        #data = ubinascii.a2b_base64(b64)
        #u0.write(b64)
        #u0.write(b'\n\n')
        #time.sleep(0.1)
        #u0.write(data)
        #time.sleep(0.1)
        #led_on_green()

    led_on()
    
    buffer = b''
    while True:
        data = u1.read()
        if data:
            buffer += data
        else:
            n_received = len(buffer)
            if not n_received:
                continue
            else:
                print(n_received, " characters received")
                print(buffer)
                n_write = n_received
                while True:
                    n_wrtten = u1.write(buffer)
                    print(n_written, ' bytes written')
                    if not n_written:
                        print("Error write to uart1")
                        break
                    elif n_written < n_write:
                        buffer = buffer[n_written:]
                        n_write -= n_written
                    else:
                        sock.send(buffer)
                        print('Sent via Ethernet')
                        break
                buffer = b''

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