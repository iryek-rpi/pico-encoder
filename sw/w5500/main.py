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

fixed_binary_key = None
settings = None
g_uart = None

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

async def send_tcp_data_async(data, reader, writer):
    writer.write(data)
    await writer.drain()
    return await reader.read(100)

async def send_serial_data_async(data, reader, writer):
    writer.write(data)
    while True:
        await asyncio.sleep_ms(nu.ASYNC_SLEEP_MS)
        b64 = reader.readline()
        if b64:
            return b64

async def process_serial_msg(uart, key, settings, dest):
    if settings[utils.CHANNEL]==c.CH_SERIAL:
        relay_reader, relay_writer = await asyncio.open_connection(settings[utils.PEER_IP], c.CRYPTO_PORT)

    try:
        while True:
            await asyncio.sleep_ms(nu.ASYNC_SLEEP_MS)
            b64 = uart.readline()
            if b64:
                sm = b64.decode('utf-8').strip()
                print(f'b64: {b64} sm: {sm}')
                if sm[:7]=='CNF_REQ':
                    saved_settings = utils.load_settings()
                    print('saved_settings: ', saved_settings)
                    str_settings = json.dumps(saved_settings)
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
                #elif sm[:7]=='TXT_WRT' and sm[-7:]=='TXT_END':
                elif settings[utils.CHANNEL]==c.CH_SERIAL:
                    msg_bin = bytes(sm, 'utf-8')
                    encoded_msg = coder.encrypt_text(msg_bin, key)
                    response=send_tcp_data_async(encoded_msg, relay_reader, relay_writer)
                    uart.write(response)
    except Exception as e:
        print(e)
        
    print('.', end='')
    return

async def process_stream(handler1, handler2, key, reader, writer, name, dest):
    print(f'handling {name}..')
    if dest==g_uart:
        relay_reader, relay_writer = g_uart, g_uart
        relay_func = send_serial_data_async
    else:
        relay_reader, relay_writer = await asyncio.open_connection(*dest)
        relay_func = send_tcp_data_async

    while True:
        b64 = await reader.read(100)
        addr = writer.get_extra_info('peername')
        print(f"Received {b64} from {addr}")
        if len(b64)>0:
            processed_msg = handler1(b64, key)
            response = await relay_func(processed_msg, relay_reader, relay_writer)
            if len(response)>0:
                processed_response = handler2(response, key)
                writer.write(processed_response)
                await writer.drain()
            else:
                break
        else:
            break

    print(f"Close the connection for {dest}")
    if dest!=g_uart:
        relay_writer.close()
        await relay_writer.wait_closed()
        relay_reader.close()
        await relay_reader.wait_closed()

    print(f"Close the connection for handle_{name}()")
    writer.close()
    await writer.wait_closed()
    reader.close()
    await reader.wait_closed()

async def handle_tcp_text(reader, writer):
    print(f"\n### handle TCP TEXT from {reader} {writer}")
    dest = (settings[utils.PEER_IP], c.CRYPTO_PORT)
    await process_stream(coder.encrypt_text, coder.decrypt_crypto, fixed_binary_key, reader, writer, 'TEXT', dest)

async def handle_crypto(reader, writer):
    print(f"\n### handle CRYPTO TEXT from {reader} {writer}")
    dest = g_uart if settings[utils.CHANNEL] == c.CH_SERIAL else (settings[utils.HOST_IP], int(settings[utils.HOST_PORT]))
    await process_stream(coder.decrypt_crypto, coder.encrypt_text, fixed_binary_key, reader, writer, 'CRYPTO', dest)

def main():
    global fixed_binary_key
    global settings
    global g_uart

    led_start()
    settings = utils.load_settings()
    print(settings)

    g_uart, settings = nu.init_connections(settings)
    fixed_binary_key = coder.fix_len_and_encode_key(settings['key'])

    loop = asyncio.get_event_loop()

    loop.create_task(process_serial_msg(g_uart, fixed_binary_key, settings))

    print(f'\n### starting CRYPTO server at {settings[utils.MY_IP]}:{c.CRYPTO_PORT}')
    loop.create_task(asyncio.start_server(handle_crypto, '0.0.0.0', c.CRYPTO_PORT))

    print('Channel: TCP') if settings[utils.CHANNEL] == c.CH_TCP else print('Channel: SERIAL')  
    if settings[utils.CHANNEL] == c.CH_TCP:
        print(f'\n### starting TEXT server at {settings[utils.MY_IP]}:{c.TEXT_PORT}')
        loop.create_task(asyncio.start_server(handle_tcp_text, '0.0.0.0', c.TEXT_PORT))

    cw.prepare_web()
    loop.create_task(asyncio.start_server(cw.server._handle_request, '0.0.0.0', 80))

    print('run_forever')
    loop.run_forever()

if __name__ == '__main__':
    main()
