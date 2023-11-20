'''
W5500 
'''
import machine
from machine import Pin
from machine import SPI
import network

import utime as time
import uasyncio as asyncio
import ujson as json

import config_web as cw
import utils
import net_utils as nu

settings = None

async def process_serial_msg(uart, channel, fixed_binary_key, settings):
    try:
        sm = uart.readline()
        if sm:
            sm = sm.decode('utf-8').strip()
            print(f'cmd: {sm[:7]}  sm[-7:]: {sm[-7:]}')
            if sm[:7]=='CNF_REQ':
                saved_settings = utils.load_settings()
                print('saved_settings: ', saved_settings)
                str_settings = json.dumps(saved_settings)
                print(len(str_settings), ' bytes : ', str_settings)
                msg = bytes('CNF_JSN', 'utf-8') + bytes(str_settings, 'utf-8') + bytes('CNF_END\n', 'utf-8')
                asyncio.sleep_ms(nu.ASYNC_SLEEP_MS)
                uart.write(msg)
            elif sm[:7]=='CNF_WRT' and sm[-7:]=='CNF_END':
                uart.deinit()
                received_settings = sm[7:-7]
                print(f'Received settings: {received_settings}')
                utils.save_settings(received_settings)
                asyncio.sleep_ms(1000)
                machine.reset()
            elif channel==utils.CH_SERIAL and sm[:7]=='TXT_WRT' and sm[-7:]=='TXT_END':
                received_msg = f'{sm[7:-7]}'
                received_msg = bytes(received_msg.strip(), 'utf-8')
                print(f'TXT_WRT Received msg: {received_msg}')
                #encoded_msg = encrypt_text(received_msg, fixed_binary_key)
                if not encoded_msg:
                    print('Encryption result Empty')
                    encoded_msg = bytes('***BAD DATA***', 'utf-8')
                await asyncio.sleep_ms(nu.ASYNC_SLEEP_MS)
                #pn.send_data_sync(encoded_msg, settings['peer_ip'], utils.ENC_PORT)
                await asyncio.sleep_ms(nu.ASYNC_SLEEP_MS)
                return
            else:
                print('Unknown command')
    except Exception as e:
        print(e)
        
    print('.', end='')
    return

async def handle_crypto(reader, writer):
    while True:
        print('handling crypto..')        
        data = await reader.read(100)
        message = data.decode()
        print(f'crypto data received:{message}')
        addr = writer.get_extra_info('peername')
        print(f"Received {message} from {addr}")

        print(f"Send: {message}")
        writer.write(data)
        await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()
    reader.close()
    await reader.wait_closed()


async def handle_tcp_text(reader, writer):
    while True:
        print('handling text..')
        data = await reader.read(100)
        message = data.decode()
        print(f'text data received:{message}')
        addr = writer.get_extra_info('peername')
        print(f"Received {message} from {addr}")

        print(f"Send: {message}")
        writer.write(data)
        await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()
    reader.close()
    await reader.wait_closed()

async def handle_serial(uart):
    while True:
        print('handling text..')
        data = await reader.read(100)
        message = data.decode()
        print(f'text data received:{message}')
        addr = writer.get_extra_info('peername')
        print(f"Received {message} from {addr}")

        print(f"Send: {message}")
        writer.write(data)
        await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()
    reader.close()
    await reader.wait_closed()

def main():
    global settings

    settings = utils.load_settings()
    uart, settings = nu.init_connections(settings)
    print('IP assigned: ', settings[utils.MY_IP])
    channel = settings[utils.CHANNEL]

    loop = asyncio.get_event_loop()
    if channel == utils.CH_TCP:
        loop.create_task(asyncio.start_server(handle_tcp_text, '0.0.0.0', 2004))
    loop.create_task(asyncio.start_server(handle_crypto, '0.0.0.0', 8513))
    loop.create_task(process_serial_msg(uart, channel, None, settings))
    cw.prepare_web()
    loop.create_task(asyncio.start_server(cw.server._handle_request, '0.0.0.0', 80))

    print('run_forever')
    loop.run_forever()

if __name__ == '__main__':
    main()
