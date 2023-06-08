from machine import Pin, Timer

import time

led = Pin('LED', Pin.OUT)
yellow = Pin(13, Pin.OUT)
green = Pin(14, Pin.OUT)
red = Pin(15, Pin.OUT)

timer_led = None
timer_yellow = None
timer_red = None
timer_green = None
    
def blink_led(_led, freq):
    global timer_led, timer_yellow, timer_green, timer_red

    if _led==led:
        timer_led.deinit()
        timer_led = None
        timer_led = Timer()
        timer_led.init(freq=freq, mode=Timer.PERIODIC, callback=blink_default_led)
    elif _led==yellow:
        timer_yellow.deinit()
        timer_yellow = None
        timer_yellow = Timer()
        timer_yellow.init(freq=freq, mode=Timer.PERIODIC, callback=blink_yellow)
    elif _led==green:
        timer_green.deinit()
        timer_green = None
        timer_green = Timer()
        timer_green.init(freq=freq, mode=Timer.PERIODIC, callback=blink_green)
    elif _led==red:
        timer_red.deinit()
        timer_red = None
        timer_red = Timer()
        timer_red.init(freq=freq, mode=Timer.PERIODIC, callback=blink_red)
    else:
        print('Error: unknown led')


def blink_default_led(timer):
    led.toggle()

def blink_yellow(timer):
    yellow.toggle()

def blink_green(timer):
    green.toggle()

def blink_red(timer):
    red.toggle()

def led_onoff(_led, onoff):
    global timer_led, timer_yellow, timer_green, timer_red

    if _led==led:
        if timer_led:
            timer_led.deinit()
            timer_led = None
        if onoff:
            led.on()
        else:
            led.off()
    elif _led==yellow:
        if timer_yellow:
            timer_yellow.deinit()
            timer_yellow = None
        if onoff:
            yellow.on()
        else:
            yellow.off()
    elif _led==green:
        if timer_green:
            timer_green.deinit()
            timer_green = None
        if onoff:
            green.on()
        else:
            green.off()
    elif _led==red:
        if timer_red:
            timer_red.deinit()
            timer_red = None
        if onoff:
            red.on()
        else:
            red.off()
    else:
        print('Error: unknown led')
