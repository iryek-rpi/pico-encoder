from machine import Pin, Timer

led = Pin('LED', Pin.OUT)
yellow = Pin(13, Pin.OUT)
red = Pin(14, Pin.OUT)
green = Pin(15, Pin.OUT)

timer_led = None
timer_yellow = None
timer_red = None
timer_green = None
    
def led_init():
    led_onoff(led, False)
    led_onoff(yellow, False)
    led_onoff(green, False)
    led_onoff(red, False)

def led_start():
    led_onoff(red, True)
    blink_led(green, 2)
    blink_led(yellow, 2)

def led_state_good():
    led_onoff(red, True)
    led_onoff(green, True)
    led_onoff(yellow, False)        

def led_state_error():
    led_onoff(green, True)
    blink_led(yellow, 2)

def led_state_no_ip():
    led_onoff(green, False)
    led_onoff(yellow, True)

def led_state_tcp_error():
    led_onoff(green, True)
    blink_led(yellow, 5) # 5Hz

def led_state_serial_error():
    led_onoff(green, True)
    blink_led(yellow, 2) # 2Hz

def led_state_reset():
    blink_led(red, 8) # 8Hz
    blink_led(green, 8) # 8Hz
    blink_led(yellow, 8) # 8Hz

def led_state_data_error():
    blink_led(green, 5)
    led_onoff(yellow, False)

def blink_led(_led, freq):  # freq = Hz
    global timer_led, timer_yellow, timer_green, timer_red

    if _led==led:
        timer_led.deinit()
        timer_led = None
        timer_led = Timer()
        timer_led.init(freq=freq, mode=Timer.PERIODIC, callback=blink_default_led)
    elif _led==yellow:
        if timer_yellow:
          timer_yellow.deinit()
        timer_yellow = None
        timer_yellow = Timer()
        timer_yellow.init(freq=freq, mode=Timer.PERIODIC, callback=blink_yellow)
    elif _led==green:
        if timer_green:
          timer_green.deinit()
        timer_green = None
        timer_green = Timer()
        timer_green.init(freq=freq, mode=Timer.PERIODIC, callback=blink_green)
    elif _led==red:
        if timer_red:
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

def all_led_onoff(onoff):
    if onoff:
        led_onoff(led, True)
        led_onoff(yellow, True)
        led_onoff(green, True)
        led_onoff(red, True)
    else:
        led_onoff(led, False)
        led_onoff(yellow, False)
        led_onoff(green, False)
        led_onoff(red, False)

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
            print('red on')
            red.on()
        else:
            red.off()
    else:
        print('Error: unknown led')
