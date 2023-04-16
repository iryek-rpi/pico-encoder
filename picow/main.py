from machine import Pin, Timer
from machine import UART
import ubinascii

import time

led = Pin('LED', Pin.OUT)
led_red = Pin(15, Pin.OUT)
led_green = Pin(14, Pin.OUT)
timer_red = Timer()
timer_green = Timer()

print('Starting script')

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=10)
    
    uart1 = UART(1, tx=Pin(6), rx=Pin(7))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=10)
    
    return uart0, uart1

def main():
    led.on()
    u0, u1 = init_serial()
    buffer = b''
    while True:
        data = u0.read()
        if data:
            led_on_green()
            led_off_red()
            buffer += data
        else:
            n_received = len(buffer)
            if not n_received:
                continue
            else:
                print(n_received), " characters received")
                print(buffer)
                n_write = n_received
                while True:
                    n_wrtten = u1.write(buffer)
                    if not n_written:
                        print("Error write to uart1")
                        break
                    elif n_written < n_write:
                        buffer = buffer[n_written:]
                        n_write -= n_written
                    else:
                        break
                buffer = b''
                    
                        
                    
                buffer = b''

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
    
if __name__ == '__main__':
    main()