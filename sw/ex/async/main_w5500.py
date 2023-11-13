'''
W5500 
'''
import machine
from machine import Pin
from machine import SPI
import network

import utime as time
import uasyncio as asyncio

def w5x00_init(ip, subnet, gateway):
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    
    nic.active(True)
    nic.ifconfig((ip, subnet, gateway,'8.8.8.8'))

    wait_count = 0
    while not nic.isconnected():
        print('Waiting for Link...')
        time.sleep_ms(500)
        wait_count += 1
        if wait_count > 10:
            return None
    
    return nic.ifconfig()

async def handle_crypto(reader, writer):
    while True:
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        print(f"Send: {message!r}")
        writer.write(data)
        await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closedro)


async def handle_text(reader, writer):
    while True:
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        print(f"Send: {message!r}")
        writer.write(data)
        await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()

async def start_serving(handler, port):
    server = await asyncio.start_server(handler, '127.0.0.1', port)
    print(f'Serving on {", ".join(str(sock.getsockname()) for sock in server.sockets)}:{port}')
    async with server:
        await server.serve_forever()

def main():
    net_info = w5x00_init('192.168.2.8', '255.255.255.0', '192.168.2.1')

    if not (net_info and net_info[0]):
        return

    print('IP assigned: ', net_info[0])

    loop = asyncio.get_event_loop()
    loop.create_task(start_serving(handle_text, 2004))
    loop.create_task(start_serving(handle_crypto, 8513))
    loop.run_forever()

if __name__ == '__main__':
    main()
