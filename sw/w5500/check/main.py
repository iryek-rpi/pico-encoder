'''Test code'''
import machine
from machine import Pin
from machine import UART
import utime

from led import *

BAUD_RATE = 9600  #19200
SERIAL_TIMEOUT = 50

print('Starting W5500 script')
led_init()
btn = Pin(9, Pin.IN, Pin.PULL_UP)

btn_pressed = 0
def btn_callback(btn):
    global btn_pressed
    print('Button pressed')
    btn_pressed = btn_pressed + 1

btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_callback)

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=BAUD_RATE, bits=8, parity=None, stop=1, timeout=SERIAL_TIMEOUT)
    return uart0

async def process_serial_msg(uart, fixed_binary_key, settings):
    sm = uart.readline()
    if sm:
        try:
            sm = sm.decode('utf-8')
            sm = sm.strip()
            print(sm)
            cmd = sm[:7]
            print(f'cmd: {cmd}')
            print(f'sm[-7:]: {sm[-7:]}')
            if cmd=='CNF_REQ':
                uart.write('CNF_WRT')
            elif cmd=='CNF_WRT' and sm[-7:]=='CNF_END':
                uart.deinit()
                uart = None
                received_settings = sm[7:-7]
                print(f'Received settings: {received_settings}')
                return
            elif cmd=='TXT_WRT' and sm[-7:]=='TXT_END':
                uart.deinit()
                uart = None
                received_msg = f'{sm[7:-7]}'
                received_msg = bytes(received_msg.strip())
                print(f'TXT_WRT Received msg: {received_msg}')
                return
            else:
                print('Unknown command')
        except Exception as e:
            print(e)
        
    print('.', end='')

    return

def main():
    global btn_pressed

    blink_led(red, 5)
    blink_led(green, 5)
    blink_led(yellow, 5)

    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    print(f'uart0: {uart0}')

    while True:
        print('waiting for button press...')
        if btn_pressed>0:
            for BAUD_RATE in [4800, 9600, 115200]:
                SERIAL_MSG = f'Hello, world! This is a test message for baud rate {BAUD_RATE}'
                uart0.init(baudrate=BAUD_RATE, bits=8, parity=None, stop=1, timeout=SERIAL_TIMEOUT)
                count = 0
                while count<10:
                    count = count + 1
                    uart0.write(SERIAL_MSG)
                    msg = uart0.readline()
                    if msg:
                        msg = msg.decode('utf-8').strip()
                        print('msg read: ', msg )
                        if msg == SERIAL_MSG:
                            print(f'BAUD_RATE {BAUD_RATE} OK')
                            if BAUD_RATE==4800:
                                led_onoff(red, True)
                            elif BAUD_RATE==9600:
                                led_onoff(green, True)
                            else:
                                led_onoff(yellow, True)
                        else:
                            print(f'BAUD_RATE {BAUD_RATE} NG')
                            if BAUD_RATE==4800:
                                led_onoff(red, False)
                            elif BAUD_RATE==9600:
                                led_onoff(green, False)
                            else:
                                led_onoff(yellow, False)
                        utime.sleep(2)
                        break
                uart0.deinit()
                utime.sleep(0.2)
            break
        utime.sleep(0.5)

    while True:
        utime.sleep(5)

if __name__ == '__main__':
    main()
