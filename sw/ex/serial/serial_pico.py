'''micropython example of serial communication between pico and pc'''
from machine import Pin, UART
import time

def uart0():
    uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
    uart.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=10)
    return uart

def rw(uart):
    while True:
        time.sleep(1)
        print("writing...")
        uart.write('t')
        if uart.any():
            data = uart.read()
            if data == b'm':
                print(f'b"m" received: {data}')
                led.toggle()
            else:
                print(data)
    #    time.sleep(1)

u0 = uart0()
print(u0)
rw(u0)
