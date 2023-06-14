'''
W5500
'''
from machine import Pin
from machine import Timer
from machine import UART
import utime

from usocket import socket

import ubinascii

interrupt_flag=0
btn = Pin(9, Pin.IN, Pin.PULL_UP)

def callback(btn):
    global interrupt_flag
    if not interrupt_flag:
        interrupt_flag=1
    else:
        interrupt_flag=0
    print('button_pressed')
    
btn.irq(trigger=Pin.IRQ_FALLING, handler=callback)


default_led = Pin('LED', Pin.OUT)
default_led_timer = Timer()
led_red = Pin(15, Pin.OUT)
led_green = Pin(14, Pin.OUT)
timer_red = Timer()
timer_green = Timer()


def main():
    blink_default_led(default_led, default_led_timer)
    led_on()
    while True:
        print('main loop')
        utime.sleep(3)


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