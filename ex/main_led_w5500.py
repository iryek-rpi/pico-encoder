from machine import Pin, Timer
import time

if __name__ == '__main__':
    default_led = None
    led_red = Pin(14, Pin.OUT)
    led_yellow = Pin(13, Pin.OUT)
    led_green = Pin(15, Pin.OUT)
    

    
    while(1):
        led_red.off()
        led_green.off()
        led_yellow.off()
        time.sleep(0.5)
        led_red.on()
        time.sleep(0.5)
        led_green.on()
        time.sleep(0.5)
        led_yellow.on()
        time.sleep(0.5)

