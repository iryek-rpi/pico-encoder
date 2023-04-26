'''
W5500
'''
from machine import Pin
from machine import Timer
from machine import UART
import utime

from usocket import socket

import network
import ubinascii

from send_tcp import w5x00_init

interrupt_flag=0
btn = Pin(13, Pin.IN, Pin.PULL_UP)

def callback2(btn):
    global interrupt_flag
    interrupt_flag=1
    # Set to Accesspoint mode
    # Change this to whatever Wifi SSID you wish
    #ap = access_point("위너스 핫스팟")
    #ip = ap.ifconfig()[0]
    # Grab the IP address and store it
    #logging.info(f"starting DNS server on {ip}")
    # # Catch all requests and reroute them
    #dns.run_catchall(ip)
    #server.run()                            # Run the server
    #logging.info("Webserver Started")    
    
def callback(btn):
    global interrupt_flag
    if not interrupt_flag:
        interrupt_flag=1
    else:
        interrupt_flag=0

btn.irq(trigger=Pin.IRQ_FALLING, handler=callback)


default_led = Pin('LED', Pin.OUT)
default_led_timer = Timer()
led_red = Pin(15, Pin.OUT)
led_green = Pin(14, Pin.OUT)
timer_red = Timer()
timer_green = Timer()

print('Starting W5500 script')

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL_TIMEOUT)

    uart1 = UART(1, tx=Pin(4), rx=Pin(5))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=10)
    
    return uart0, uart1

def main():
    blink_default_led(default_led, default_led_timer)
    led_on_red()
    led_on_green()
    u0, u1 = init_serial()

    w5x00_init('192.168.1.20')

    sock = socket()
    print('connecting to peer through socket: ', sock)
    sock.connect(('192.168.1.10', 5002))
    led_on()

    buffer = b''
    while True:
        data = u1.read()
        if data:
            buffer += data
        else:
            if not buffer:
                continue
            else:
                n_to_write = len(buffer)
                print(n_to_write, " characters received")
                print(buffer)
                while True:
                    n_written = u1.write(buffer)
                    print(n_written, ' bytes written')
                    if not n_written:
                        print("Error write to uart1")
                        break
                    elif n_written < n_to_write:
                        buffer = buffer[n_written:]
                        n_to_write -= n_written
                    else:
                        sock.send(buffer)
                        print('Sent via Ethernet')
                        break
                buffer = b''

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