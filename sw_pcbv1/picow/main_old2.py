from machine import Pin, Timer
from machine import UART
import ubinascii

import time

SERIAL_TIMEOUT = 5 # ms

led = Pin('LED', Pin.OUT)
led_red = Pin(15, Pin.OUT)
led_green = Pin(14, Pin.OUT)
timer_red = Timer()
timer_green = Timer()

print('Starting script')

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL_TIMEOUT)

    uart1 = UART(1, tx=Pin(4), rx=Pin(5))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL_TIMEOUT)

    return uart0, uart1

def main():
    led.on()
    led_on_green()
    spc, seth = init_serial()
    buf2eth = b''
    buf2pc = b''

    while True:
        data2eth = spc.read()
        if data2eth:
            led_blink_red()
            print(buf2eth)
            buf2eth += data2eth
            print(buf2eth)
        else:
            if buf2eth:
                buf2eth = ubinascii.hexlify(buf2eth)
                n_to_write = len(buf2eth)
                #buf2eth = ubinascii.a2b_base64(buf2eth)
                while True:
                    n_written = seth.write(buf2eth)
                    if not n_written:
                        print("Error write to uart1")
                        break
                    elif n_written < n_to_write:
                        buf2eth = buf2eth[n_written:]
                        n_to_write -= n_written
                    else:
                        break
                buf2eth = b''
            else:
                data2pc = seth.read()
                if data2pc:
                    led_blink_red()
                    print('buf2pc: ', buf2pc)
                    buf2pc += data2pc
                    print('buf2pc: ', buf2pc)
                else:
                    if buf2pc:
                        buf2pc = ubinascii.unhexlify(buf2pc)                        
                        n_to_write = len(buf2pc)
                        while True:
                            n_written = spc.write(buf2pc)
                            if not n_written:
                                print("Error write to uart0")
                                break
                            elif n_written < n_to_write:
                                buf2pc = buf2pc[n_written:]
                                n_to_write -= n_written
                            else:
                                break
                        buf2pc = b''

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

def blink_red(t):
    led_red.toggle()

def blink_green(t):
    led_green.toggle()

def led_blink_red():
    timer_red.init(freq=10, mode=Timer.PERIODIC, callback=blink_red)

def led_blink_green():
    timer_red.init(freq=10, mode=Timer.PERIODIC, callback=blink_green)

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