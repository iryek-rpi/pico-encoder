from machine import Pin, Timer
from machine import SPI
from machine import UART
from usocket import socket
import network
import uasyncio as asyncio

import utime

async def w5x00_init_async(json_settings):
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    nic.active(True)

    net_config = None
    if not json_settings['dhcp']:
        net_config = (json_settings['ip'], json_settings['subnet'], json_settings['gateway'])
        
    if not net_config:
        nic.ifconfig('dhcp')
    else:
        nic.ifconfig((net_config[0], net_config[1], net_config[2],'8.8.8.8'))

    while not nic.isconnected():
        print(nic.regs())
        print('Waiting for Link...')
        await asyncio.sleep(2)
    
    ifc = nic.ifconfig()
    print(ifc)
    return ifc
