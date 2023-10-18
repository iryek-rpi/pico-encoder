from machine import Pin, Timer
from machine import SPI
from machine import UART
from usocket import socket
import network
import ubinascii

import time

default_led = None
default_led_timer = None


led_red = Pin(15, Pin.OUT)
led_green = Pin(14, Pin.OUT)
timer_red = Timer()
timer_green = Timer()
    
def blink_led(led, led_timer):
    global default_led
    global default_led_timer
    
    default_led = led
    default_led_timer = led_timer
    led_timer.init(freq=0.2, mode=Timer.PERIODIC, callback=blink_led)

def blink_led(timer):
    default_led.toggle()

def led_on():
    default_led_timer.deinit()
    default_led.on()

def led_off():
    default_led_timer.deinit()
    default_led.off()

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
