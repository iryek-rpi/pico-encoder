from machine import Pin, Timer
from machine import SPI
from machine import UART
from usocket import socket
import network
import ubinascii

import time

led_red = Pin(15, Pin.OUT)
led_green = Pin(14, Pin.OUT)
timer_red = Timer()
timer_green = Timer()

def w5x00_init(ip):
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    nic.active(True)
    if not ip:
        nic.ifconfig('dhcp')
    else:
        nic.ifconfig((ip,'255.255.255.0','192.168.2.1','8.8.8.8'))

    while not nic.isconnected():
        time.sleep(1)
        print(nic.regs())
    print(nic.ifconfig())

def blink_red(timer):
    led_red.toggle()

def blink_green(timer):
    led_green.toggle()

def led_blink_red():
    timer_red.init(freq=1.5, mode=Timer.PERIODIC, callback=blink_red)

def led_blink_green():
    timer_red.init(freq=1.5, mode=Timer.PERIODIC, callback=blink_green)

def led_on_red():
    timer_red.deinit()
    led_red.on()

def led_on_green():
    timer_red.deinit()
    led_green.on()

def led_off_red():
    timer_red.deinit()
    led_red.off()

def led_off_green():
    timer_red.deinit()
    led_green.off()

def init_serial():
    uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), timeout=1)
    uart.init(bits=8, parity=None, stop=1)
    return uart

def main():

    led_blink_red()

    #w5x00_init('192.168.1.20')
    w5x00_init(None)

    time.sleep(0.5)
    s = socket()
    
    print('connecting to peer through socket:', socket)
    #s.connect(('192.168.1.166', 5001))
    time.sleep(2)
    s.connect(('192.168.1.10', 5001))

    print('init serial')
    u0 = init_serial()
    print('serial device: ', u0)
    
    led_off_red()
    #led_on_green()

    while True:
        if u0.any():
            data = u0.read(16)
            print("data from pc: ", data)
            if data:
                b64 = ubinascii.b2a_base64(data)
                s.send(b64)
                print("data sent: ", b64)
                print()
