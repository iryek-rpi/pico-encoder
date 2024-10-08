from machine import Pin, UART
import time

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
uart.init(bits=8, parity=None, stop=2)
led = Pin("LED", Pin.OUT)

while True:
    uart.write('tx')
    if uart.any():
        data = uart.read()
        if data == b'm':
            print(f'b"m" received: {data}')
            led.toggle()
        else:
            print(data)
#    time.sleep(1)