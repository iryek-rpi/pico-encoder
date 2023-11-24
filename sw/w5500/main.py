'''
W5500 
'''
import machine
from machine import Pin

import utime as time
import uasyncio as asyncio
import ujson as json

import constants as c
import config_web as cw
import net_utils as nu
import utils
from led import *
import coder

led_init()
btn = Pin(9, Pin.IN, Pin.PULL_UP)
settings = None

def btn_callback(btn):
    print('Button pressed')
    led_state_setting()
    settings = utils.load_settings()
    settings[utils.CONFIG] = 0 if settings[utils.CONFIG]==1 else 0
    utils.save_settings(settings)
    time.sleep_ms(500)
    machine.reset()

btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_callback)

async def process_serial_msg(uart, channel, fixed_binary_key, settings):
    try:
        while True:
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
                    utils.save_settings(json.loads(received_settings))
                    asyncio.sleep_ms(1000)
                    machine.reset()
                elif channel==c.CH_SERIAL and sm[:7]=='TXT_WRT' and sm[-7:]=='TXT_END':
                    received_msg = f'{sm[7:-7]}'
                    received_msg = bytes(received_msg.strip(), 'utf-8')
                    print(f'TXT_WRT Received msg: {received_msg}')
                    #encoded_msg = encrypt_text(received_msg, fixed_binary_key)
                    if not encoded_msg:
                        print('Encryption result Empty')
                        encoded_msg = bytes('***BAD DATA***', 'utf-8')
                    await asyncio.sleep_ms(nu.ASYNC_SLEEP_MS)
                    #pn.send_data_sync(encoded_msg, settings['peer_ip'], c.CRYPTO_PORT)
                    await asyncio.sleep_ms(nu.ASYNC_SLEEP_MS)
                    return
                else:
                    print('Unknown command')
    except Exception as e:
        print(e)
        
    print('.', end='')
    return

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
    process_stream(coder.encrypt_text, fixed_binary_key, reader, writer, 'TEXT', utils.PEER_IP, c.CRYPTO_PORT)

async def handle_crypto(reader, writer):
    process_stream(coder.decrypt_text, fixed_binary_key, reader, writer, 'CRYPTO', utils.HOST_IP, utils.HOST_PORT)

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
    global fixed_binary_key
    global settings

    led_start()
    settings = utils.load_settings()
    print(settings)

    uart, settings = nu.init_connections(settings)
    channel = settings[utils.CHANNEL]
    if channel == c.CH_TCP: print('Channel: TCP')
    else: print('channel: SERIAL')

    fixed_binary_key = coder.fix_len_and_encode_key(settings['key'])

    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.start_server(handle_crypto, '0.0.0.0', c.CRYPTO_PORT))
    loop.create_task(process_serial_msg(uart, channel, None, settings))
    if channel == c.CH_TCP:
        loop.create_task(asyncio.start_server(handle_tcp_text, '0.0.0.0', c.TEXT_PORT))
    cw.prepare_web()
    loop.create_task(asyncio.start_server(cw.server._handle_request, '0.0.0.0', 80))

    print('run_forever')
    loop.run_forever()

if __name__ == '__main__':
    main()
