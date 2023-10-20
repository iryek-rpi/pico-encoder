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

    u0 = init_serial()

    w5x00_init('192.168.1.20')
    s = socket()
    s.bind(('192.168.1.20', 5001))
    s.listen(5)

    led_off_red()
    led_on_green()

    conn, addr = s.accept()
    print('Connected by ', conn, 'from ', addr)

    while True:
        b64 = conn.recv(1024)
        led_blink_green()
        data = ubinascii.a2b_base64(b64)
        u0.write(b64)
        u0.write(b'\n\n')
        time.sleep(0.1)
        u0.write(data)
        time.sleep(0.1)
        led_on_green()
