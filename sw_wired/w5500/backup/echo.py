from machine import Pin, Timer
from machine import SPI
import utime
from usocket import socket
import network

import uasyncio
from w5500 import w5x00_init

async def tcp_echo_client(message):
    reader, writer = await uasyncio.open_connection('127.0.0.1', 8888)

    print('Send: ', message)
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print('Received: ', data.decode())

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
nic.active(True)
utime.sleep(2)


uasyncio.run(tcp_echo_client('Hello World!'))