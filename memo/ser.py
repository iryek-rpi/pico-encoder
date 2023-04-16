from machine import Pin, UART
import time

def uart0():
    uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
    uart.init(bits=8, parity=None, stop=1)
    return uart

def uart1():
    uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
    uart.init(bits=8, parity=None, stop=1)
    return uart

def rw(uart):
    while True:
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