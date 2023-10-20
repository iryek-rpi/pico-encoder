from machine import Pin, Timer
from machine import UART
import ubinascii

import time

led = Pin('LED', Pin.OUT)
led_red = Pin(15, Pin.OUT)
led_green = Pin(14, Pin.OUT)
timer_red = Timer()
timer_green = Timer()

def init_serial():
    uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), timeout=1)
    uart.init(bits=8, parity=None, stop=1)
    return uart

def main():
    led.on()
    u0 = init_serial()

    while True:
        n_recv = u0.any()
        if n_recv:
            led_on_green()
            led_off_red()
            data = u0.read(n_recv)
            if data:
                print(data)
                print()
                #b64 = ubinascii.b2a_base64(data)
                #s.send(b64)
        else:
            led_off_green()
            led_on_red()

    while 0:
        #b64 = conn.recv(1024)
        data = ubinascii.a2b_base64(b64)
        u0.write(b64)
        u0.write(b'\n\n')
        time.sleep(0.1)
        u0.write(data)
        time.sleep(0.1)

        led_blink_green()
        led_blink_red()

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