from machine import Pin, Timer
from machine import SPI
from machine import UART
from usocket import socket
import network

import time

def get_nic():
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    return nic

def get_mac():
    nic = get_nic()
    m = nic.config('mac')
    h = m.hex()
    print(f'mac: {m} {h}')
    return m, h

def save_mac(id=None):
    m, h = get_mac()
    filename = f'mac_{id}.bin' if id else 'mac.bin'
    with open(filename, 'wb') as f:
        f.write(m)
        return m, h
        
def read_mac(id=None):
    filename = f'mac_{id}.bin' if id else 'mac.bin'
    with open(filename, 'rb') as f:
        m = f.read()
        h = m.hex()
        return m, h
    
def w5x00_init(net_config):
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    
    nic.active(True)
    
    if not net_config:
        nic.ifconfig('dhcp')
    else:
        nic.ifconfig((net_config[0], net_config[1], net_config[2],'8.8.8.8'))

    wait_count = 0
    while not nic.isconnected():
        print(nic.regs())
        print('Waiting for Link...')
        time.sleep(1)
        wait_count += 1
        if wait_count > 10:
            return None
    
    ifc = nic.ifconfig()
    print(ifc)
    return ifc

if __name__ == '__main__':
    id = 1
    m, h = save_mac(id)
    m2, h2 = read_mac(id)
    if m != m2:
        print('Error: macs do not match')
    else:
        print('macs match')
    #read_mac()