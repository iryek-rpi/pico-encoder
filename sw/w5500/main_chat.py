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
g_settings = None
g_uart = None
g_text = []
g_crypto = []

led_init()
btn = Pin(9, Pin.IN, Pin.PULL_UP)

def btn_callback(btn):
    global g_settings

    led_state_reset()
    print('Button pressed')
    utils.init_settings()
    g_settings = utils.load_settings()
    time.sleep_ms(500)
    machine.reset()

btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_callback)

async def open_relay_connection(ip, port):
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            print(f'### open_relay_connection to {ip}:{port}')
            return reader, writer
        except Exception as e:
            led_state_tcp_error()
            print(e)
            await asyncio.sleep_ms(nu.ASYNC_SLEEP_100MS)

async def send_tcp_data_async(data, reader, writer):
    print(f'send_tcp_data_async: {data}')
    writer.write(data)
    await writer.drain()
    data = await reader.read(nu.MAX_MSG)
    print(f'send_tcp_data_async: read: {data.decode("utf-8")}')
    #return data.decode('utf-8')
    return data

async def send_serial_data_async(data, reader, writer):
    print(f'\n+++ send_serial_data_async: writer.write(data:{data}) via uart')
    writer.write(data)
    while True:
        await asyncio.sleep_ms(nu.ASYNC_SLEEP_30MS)
        b64 = reader.read(nu.MAX_MSG)
        if b64:
            print(f'+++ send_serial_data_async: reader.read({nu.MAX_MSG}) => b64:{b64}')
            return b64

def send_serial_data_sync(data, uart):
    print(f'\n@@@@@ send_serial_data_sync: writer.write(data:{data}) via uart')
    uart.write(data)
    while True:
        b64 = uart.read(nu.MAX_MSG)
        if b64:
            print(f'@@@@@ send_serial_data_sync: reader.read({nu.MAX_MSG}) => b64:{b64}')
            return b64

async def process_serial_msg(uart, key, settings):
    relay_reader = relay_writer = None
    try:
        while True:
            await asyncio.sleep_ms(nu.ASYNC_SLEEP_30MS)
            b64 = uart.readline()
            if b64:
                sm = b64.decode('utf-8').strip()
                print(f'b64: {b64} sm: {sm}')
                if sm[:7]=='CNF_REQ':
                    str_settings = json.dumps(g_settings)
                    msg = bytes('CNF_JSN', 'utf-8') + bytes(str_settings, 'utf-8') + bytes('CNF_END\n', 'utf-8')
                    asyncio.sleep_ms(nu.ASYNC_SLEEP_30MS)
                    uart.write(msg)
                elif sm[:7]=='CNF_WRT' and sm[-7:]=='CNF_END':
                    uart.deinit()
                    received_settings = sm[7:-7]
                    print(f'Received settings: {received_settings}')
                    utils.save_settings(json.loads(received_settings))
                    asyncio.sleep_ms(1000)
                    machine.reset()
                elif settings[c.CHANNEL]==c.CH_SERIAL:
                    msg_bin = bytes(sm, 'utf-8')
                    encoded_msg = coder.encrypt_text(msg_bin, key)
                    
                    if not relay_reader:
                        relay_reader, relay_writer = await open_relay_connection(settings[c.PEER_IP], c.TEXT_PORT)
                    relay_writer.write(encoded_msg)
                    await relay_writer.drain()
                    response = await relay_reader.read(nu.MAX_MSG)
                    print(f'process_serial_msg: response: {response}:{type(response)} writing to uart')
                    response = coder.decrypt_crypto(response, key)
                    print(f'decryped serial response: {response}:{type(response)} writing to uart')
                    uart.write(response)
    except Exception as e:
        led_state_serial_error()
        print(e)
        machine.reset()
        
    print('.', end='')
    return

async def process_server(handler, key, reader, writer, name, dest):
    global g_crypto
    global g_text

    print(f'\n=== process_stream: handling {name}..')
    while True:
        try:
            b64 += await reader.read(nu.MAX_MSG)
            addr = writer.get_extra_info('peername')
            print(f"\n=== process_stream() Received {b64} from {addr}")
            if len(b64)>0:
                processed_msg = handler(b64, key)
                if dest==g_uart:
                    print(f'=== process_stream: sending to serial: {processed_msg}')
                    response = send_serial_data_sync(processed_msg, g_uart)
                else:
                    print(f'=== process_stream: relaying to {dest}: {processed_msg}')
                    if handler==coder.encrypt_text:
                        g_crypto.append(processed_msg)
                    else:
                        g_text.append(processed_msg)
            if handler==coder.encrypt_text:
                bufs = g_text
            else:
                bufs = g_crypto
            
            while bufs:
                b, bufs = bufs[0], bufs[1:]
                if b:
                    writer.write(b)
                    await writer.drain()
        except Exception as e:
            print(f'=== process_stream: exception: {e}')
            break

    print(f"Close writer for handle_{name}()")
    writer.close()
    await writer.wait_closed()
    print(f"Close reader for handle_{name}()")
    reader.close()
    await reader.wait_closed()
    machine.reset()

async def process_client(handler, dest):
    global g_crypto
    global g_text

    print(f'\n=== process_client: relay opening connection to {dest}')
    relay_reader, relay_writer = await asyncio.open_connection(*dest)
    print(f'\n=== process_client: relay connection to {dest} opened')

    while True:
        if dest[1]==g_settings[c.TEXT_PORT]: # to peer
            bufs = g_crypto
        else:                                # to host
            bufs = g_text
        
        while bufs:
            b, bufs = bufs[0], bufs[1:]
            if b:
                relay_writer.write(b)
                await relay_writer.drain()

    if dest!=g_uart:
        relay_reader, relay_writer = await asyncio.open_connection(*dest)
        print(f'\n=== process_stream: relay open connection to {dest}')


async def handle_tcp_text(reader, writer):
    print("\n### handle encrypting Plain TEXT from TCP stream")
    dest = (g_settings[c.PEER_IP], c.TEXT_PORT)
    await process_server(coder.encrypt_text, fixed_binary_key, reader, writer, 'TEXT', dest)

async def handle_crypto(reader, writer):
    print("\n### handle decrypting CRYPTO TEXT from TCP stream")
    dest = g_uart if g_settings[c.CHANNEL] == c.CH_SERIAL else (g_settings[c.HOST_IP], int(g_settings[c.HOST_PORT]))
    await process_server(coder.decrypt_crypto, fixed_binary_key, reader, writer, 'CRYPTO', dest)

def main():
    global fixed_binary_key
    global g_settings
    global g_uart

    led_start()
    device_id = utils.get_device_id()
    g_settings = utils.load_settings()
    g_settings[c.DEVICE_ID] = device_id
    cw.web_settings = g_settings
    print(g_settings)

    g_uart, g_settings, ip_assigned = nu.init_connections(g_settings)
    fixed_binary_key = coder.fix_len_and_encode_key(g_settings['key'])

    loop = asyncio.get_event_loop()

    loop.create_task(process_serial_msg(g_uart, fixed_binary_key, g_settings))

    if ip_assigned:
        print('Channel: TCP') if g_settings[c.CHANNEL] == c.CH_TCP else print('Channel: SERIAL')  
        if g_settings[c.CHANNEL] == c.CH_TCP:
            print(f'\n### starting Encryption server at {g_settings[c.MY_IP]}:{c.CRYPTO_PORT}')
            loop.create_task(asyncio.start_server(handle_tcp_text, '0.0.0.0', c.CRYPTO_PORT))

        print(f'\n### starting relaying client to Decryption server {g_settings[c.PEER_IP]}, {g_settings[c.TEXT_PORT]}')
        loop.create_task(process_client(coder.decrypt_crypto, (g_settings[c.PEER_IP], c.TEXT_PORT)))
        #loop.create_task(process_client_read(coder.decrypt_crypto, (g_settings[c.PEER_IP], c.TEXT_PORT)))

        print(f'\n### starting Decryption server at {g_settings[c.MY_IP]}:{c.TEXT_PORT}')
        loop.create_task(asyncio.start_server(handle_crypto, '0.0.0.0', c.TEXT_PORT))
        if g_settings[c.CHANNEL] == c.CH_TCP:
            print(f'\n### starting relaying client to Host')
            loop.create_task(process_client( coder.encrypt_text, (g_settings[c.HOST_IP], int(g_settings[c.HOST_PORT]))))
            #loop.create_task(process_client_read( coder.encrypt_text, (g_settings[c.HOST_IP], int(g_settings[c.HOST_PORT]))))

        cw.prepare_web()
        loop.create_task(asyncio.start_server(cw.server._handle_request, '0.0.0.0', 80))
    else:
        loop.create_task(nu.w5x00_init_async((g_settings[c.MY_IP], g_settings[c.SUBNET], g_settings[c.GATEWAY])))

    print('run_forever')
    loop.run_forever()

if __name__ == '__main__':
    main()
