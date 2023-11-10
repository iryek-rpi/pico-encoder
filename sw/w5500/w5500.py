from machine import Pin, Timer
from machine import SPI
from machine import UART
from usocket import socket
import network

import utime

def w5x00_init(net_config):
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    
    nic.active(True)
    nic.ifconfig((net_config[0], net_config[1], net_config[2],'8.8.8.8'))

    wait_count = 0
    while not nic.isconnected():
        print(nic.regs())
        print('Waiting for Link...')
        utime.sleep_ms(1000)
        wait_count += 1
        if wait_count > 10:
            return None
    
    ifc = nic.ifconfig()
    print(ifc)
    return ifc
