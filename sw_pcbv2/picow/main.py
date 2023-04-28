from machine import Pin
from machine import Timer
from machine import UART
import ubinascii

import utime
import utils

SERIAL_TIMEOUT = 100 # ms

led = Pin('LED', Pin.OUT)


def init_serial():
    uart1 = UART(1, tx=Pin(4), rx=Pin(5))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL_TIMEOUT)

    return uart1

def main():    
    s1 = init_serial()

    json_settings = utils.load_json_settings()
    print(json_settings)
    len_json = len(json_settings)
    len_json = bytes(f'{len_json}\n', 'utf-8')
    print(len_json)

    while True:
        srecv = s1.readline()
        while True:
            print(srecv)
            if srecv and srecv.decode('utf-8')=='READY':
                break
            srecv = s1.readline()

        print('PEER READY')

        s1.write(len_json)

        result = True
        srecv = s1.readline()
        while True:
            print(srecv)
            if srecv:
                if srecv.decode('utf-8')=='READY':
                    break
                elif srecv.decode('utf-8')=='FAIL':
                    result=False
                    break
            srecv = s1.readline()

        if not result:
            continue
        print('PEER READY 2')

        nw = s1.write(json_settings)
        print(f'written: {nw}')

        srecv = s1.readline()
        print(srecv)
        while True:
            if srecv and srecv.decode('utf-8')=='READY':
                break
            srecv = s1.readline()
            print(srecv)

        print('PEER READY')

    led.on()

    return

if __name__ == "__main__":
    main()