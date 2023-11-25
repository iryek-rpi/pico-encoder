'''
W5500 
'''
import machine
from machine import Pin, SPI

import utime as time
import uasyncio as asyncio
import network

async def process_stream(handler, key, reader, writer, name, dest_ip, dest_port):
    print(f'handling {name}..')
    b64 = await reader.readline()
    addr = writer.get_extra_info('peername')
    message = b64.decode()
    print(f'{name} data received:{message}')
    print(f"Received {message} from {addr}")
    processed_msg = handler(b64, key)

    sr, sw = await asyncio.open_connection(dest_ip, dest_port)
    print(f'write {processed_msg} to {dest_ip}:{dest_port}')
    sw.write(processed_msg)
    await sw.drain()
    sw.close()
    await sw.wait_closed()
    sr.close()
    await sr.wait_closed()

    print(f"Close the connection for handle_{name}()")
    writer.close()
    await writer.wait_closed()
    reader.close()
    await reader.wait_closed()

async def handle_tcp_text(reader, writer):
    print(f"\n### handle TCP TEXT from {reader} {writer}")
    #process_stream(coder.encrypt_text, fixed_binary_key, reader, writer, 'TEXT', utils.PEER_IP, c.CRYPTO_PORT)

async def handle_crypto(reader, writer):
    print(f"\n### handle CRYPTO TEXT from {reader} {writer}")
    #process_stream(coder.decrypt_text, fixed_binary_key, reader, writer, 'CRYPTO', utils.HOST_IP, utils.HOST_PORT)

def w5x00_init(net_config):
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    
    nic.active(True)
    nic.ifconfig((net_config[0], net_config[1], net_config[2],'8.8.8.8'))

    wait_count = 0
    while not nic.isconnected():
        print(nic.regs())
        print('Waiting for Link...')
        time.sleep_ms(1000)
        wait_count += 1
        if wait_count > 10:
            return None
    
    ifc = nic.ifconfig()
    print(ifc)
    return ifc

def main():
    ip, subnet, gateway, _ = w5x00_init(('192.168.2.9', '255.255.255.0', '192.168.2.1'))
    print(f'assigned {ip} {subnet} {gateway}')

    loop = asyncio.get_event_loop()

    print(f'\n### starting CRYPTO server at {ip}:{8502}')
    loop.create_task(asyncio.start_server(handle_crypto, '0.0.0.0', 8502))

    print(f'\n### starting TEXT server at {ip}:{8501}')
    loop.create_task(asyncio.start_server(handle_tcp_text, '0.0.0.0', 8501))

    print('run_forever')
    loop.run_forever()

if __name__ == '__main__':
    main()
