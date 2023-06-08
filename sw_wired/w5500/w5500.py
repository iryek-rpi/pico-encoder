from machine import Pin, Timer
from machine import SPI
from machine import UART
from usocket import socket
import network

import time

def w5x00_init(ip):
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    nic.active(True)
    if not ip:
        nic.ifconfig('dhcp')
    else:
        nic.ifconfig((ip,'255.255.255.0', ip,'8.8.8.8'))

    while not nic.isconnected():
        print(nic.regs())
        print('Waiting for Link...')
        time.sleep(1)
    ifc = nic.ifconfig()
    print(ifc)
    return ifc[0]
