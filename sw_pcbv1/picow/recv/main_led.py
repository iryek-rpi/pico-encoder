from machine import Pin
import time

p14 = Pin(14, Pin.OUT)
p15 = Pin(15, Pin.OUT)
led = Pin('LED', Pin.OUT)

led.on()

time.sleep(5)
p14.on()
p15.on()
time.sleep(5)
p14.off()
p15.off()
time.sleep(5)

while 1:
    p14.on()
    time.sleep(0.2)
    p15.on()
    time.sleep(0.2)
    p14.off()
    time.sleep(0.2)
    p15.off()
    time.sleep(0.2)