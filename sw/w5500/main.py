'''
W5500 
'''
import machine
from machine import Pin
import utime
import gc
import ujson
import uasyncio

import config_web as cw

import mpyaes as aes
import coder
from led import *
import utils
import pico_net as pn


print('Starting main script')
led_init()
btn = Pin(9, Pin.IN, Pin.PULL_UP)
gc_start_time = utime.ticks_ms()

def btn_callback(btn):
    print('Button pressed')
    led_state_setting()
    settings = utils.load_settings()
    settings[utils.CONFIG] = 0 if settings[utils.CONFIG]==1 else 0
    utils.save_settings(settings)
    utime.sleep_ms(500)
    machine.reset()

btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_callback)

def encrypt_text(b64, fixed_binary_key):
    print('data received: ', b64)
    print('type(b64): ', type(b64))
    
    print('msg: ', b64)
    IV = aes.generate_IV(16)
    print('fixed_binary_key: ', fixed_binary_key, 'type(fixed_binary_key): ', type(fixed_binary_key))
    cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    msg = cipher.encrypt(b64)
    print('IV:', IV, ' msg:', msg)
    return IV + msg

def decrypt_crypto(b64, fixed_binary_key):
    print('data received: ', b64)
    print('type(b64): ', type(b64))
    
    print('b64: ', b64)
    IV, msg = b64[:16], b64[16:]
    print('IV:', IV, ' msg:', msg)
    msg_ba = bytearray(msg)
    cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
    return cipher.decrypt(msg_ba)

#async def process_tcp_msg(b64, handler, channel, uart, dest_ip, dest_port, fixed_binary_key):
def process_tcp_msg(b64, handler, channel, uart, dest_ip, dest_port, fixed_binary_key):
    processed_msg = handler(b64, fixed_binary_key)
    if not processed_msg:
        print('TCP processed result Empty')
        processed_msg = bytes('***BAD DATA***', 'utf-8')
    if channel == utils.CH_TCP:
        print('sending processed msg: ', processed_msg, ' to ', dest_ip, ':', dest_port)
        pn.send_data(processed_msg, dest_ip, dest_port)
        #await pn.send_data(processed_msg, dest_ip, dest_port)
    else:
        print('sending processed msg: ', processed_msg, ' to ', uart)
        uart.write(processed_msg)

def process_serial_msg_sync(uart, fixed_binary_key, settings):
    try:
        sm = uart.readline()
        #print(f'sm: {sm}')
        if sm:
            sm = sm.decode('utf-8').strip()
            print(f'cmd: {sm[:7]}  sm[-7:]: {sm[-7:]}')
            if sm[:7]=='CNF_REQ':
                saved_settings = utils.load_settings()
                print('saved_settings: ', saved_settings)
                str_settings = ujson.dumps(saved_settings)
                print(len(str_settings), ' bytes : ', str_settings)
                msg = bytes('CNF_JSN', 'utf-8') + bytes(str_settings, 'utf-8') + bytes('CNF_END\n', 'utf-8')
                uart.write(msg)
            elif sm[:7]=='CNF_WRT' and sm[-7:]=='CNF_END':
                uart.deinit()
                received_settings = sm[7:-7]
                print(f'Received settings: {received_settings}')
                utils.save_settings(received_settings)
                utime.sleep_ms(1000)
                machine.reset()
            elif sm[:7]=='TXT_WRT' and sm[-7:]=='TXT_END':
                received_msg = f'{sm[7:-7]}'
                received_msg = bytes(received_msg.strip(), 'utf-8')
                print(f'TXT_WRT Received msg: {received_msg}')
                encoded_msg = encrypt_text(received_msg, fixed_binary_key)
                if not encoded_msg:
                    print('Encryption result Empty')
                    encoded_msg = bytes('***BAD DATA***', 'utf-8')
                #await uasyncio.sleep_ms(pn.ASYNC_SLEEP_MS)
                pn.send_data_sync(encoded_msg, settings['peer_ip'], utils.ENC_PORT)
                #await uasyncio.sleep_ms(pn.ASYNC_SLEEP_MS)
                return
            else:
                print('Unknown command')
    except Exception as e:
        print(e)
        
    print('.', end='')

    return

async def process_serial_msg(uart, fixed_binary_key, settings):
    try:
        sm = uart.readline()
        if sm:
            sm = sm.decode('utf-8').strip()
            print(f'cmd: {sm[:7]}  sm[-7:]: {sm[-7:]}')
            if sm[:7]=='CNF_REQ':
                saved_settings = utils.load_settings()
                print('saved_settings: ', saved_settings)
                str_settings = ujson.dumps(saved_settings)
                print(len(str_settings), ' bytes : ', str_settings)
                msg = bytes('CNF_JSN', 'utf-8') + bytes(str_settings, 'utf-8') + bytes('CNF_END\n', 'utf-8')
                uart.write(msg)
            elif sm[:7]=='CNF_WRT' and sm[-7:]=='CNF_END':
                uart.deinit()
                received_settings = sm[7:-7]
                print(f'Received settings: {received_settings}')
                utils.save_settings(received_settings)
                utime.sleep_ms(1000)
                machine.reset()
            elif sm[:7]=='TXT_WRT' and sm[-7:]=='TXT_END':
                received_msg = f'{sm[7:-7]}'
                received_msg = bytes(received_msg.strip(), 'utf-8')
                print(f'TXT_WRT Received msg: {received_msg}')
                encoded_msg = encrypt_text(received_msg, fixed_binary_key)
                if not encoded_msg:
                    print('Encryption result Empty')
                    encoded_msg = bytes('***BAD DATA***', 'utf-8')
                await uasyncio.sleep_ms(pn.ASYNC_SLEEP_MS)
                pn.send_data_sync(encoded_msg, settings['peer_ip'], utils.ENC_PORT)
                await uasyncio.sleep_ms(pn.ASYNC_SLEEP_MS)
                return
            else:
                print('Unknown command')
    except Exception as e:
        print(e)
        
    print('.', end='')

    return

async def process_serial_config_msg(uart, settings):
    try:
        sm = uart.readline()
        if sm:
            sm = sm.decode('utf-8').strip()
            print(f'cmd: {sm[:7]}  sm[-7:]: {sm[-7:]}')
            if sm[:7]=='CNF_REQ':
                saved_settings = utils.load_settings()
                print('saved_settings: ', saved_settings)
                str_settings = ujson.dumps(saved_settings)
                print(len(str_settings), ' bytes : ', str_settings)
                msg = bytes('CNF_JSN', 'utf-8') + bytes(str_settings, 'utf-8') + bytes('CNF_END\n', 'utf-8')
                uart.write(msg)
            elif sm[:7]=='CNF_WRT' and sm[-7:]=='CNF_END':
                uart.deinit()
                received_settings = sm[7:-7]
                print(f'Received settings: {received_settings}')
                received_settings[utils.CONFIG] = 0
                utils.save_settings(received_settings)
                await uasyncio.sleep_ms(200)
                machine.reset()
            else:
                print('Unknown command')
    except Exception as e:
        print(e)
        
    print('.', end='')

    return

async def run_serial_config_server(uart, settings):
    while True:
        await uasyncio.sleep_ms(pn.ASYNC_SLEEP_MS)
        await process_serial_config_msg(uart, settings)
            #gc_start_time = utils.garbage_collect(gc_start_time)

    pn.close_sockets(serv_sock_text, serv_sock_crypto, conn_text, conn_crypto)
    if uart:
        uart.deinit()

    led_onoff(green, False)
    print("Waiting for 0.2 sec before reset...")
    utime.sleep_ms(200)
    machine.reset()

def run_hybrid_server_sync(uart, fixed_binary_key, settings):
    sock_crypto = pn.init_serv_socket(settings[utils.MY_IP], utils.ENC_PORT)
    crypto_conn = None

    crypto_connected = False
    while True:
        if not crypto_conn:
            crypto_poller = select.poll()
            crypto_poller.register(sock_crypto, select.POLLIN)
            res = crypto_poller.poll(50)
            if res:
                crypto_conn, addr = sock_crypto.accept()
        else:
            crypto_conn_poller = select.poll()
            res = crypto_conn_poller.poll(50)
            if res:
                b64 = crypto_conn.recv(32)
                if b64:
                    process_tcp_msg(b64, decrypt_crypto, settings[utils.CHANNEL], None, settings['host_ip'], settings['host_port'], fixed_binary_key)
                else:
                    crypto_conn = pn.close_server_socket(conn_crypto, tcp_poller)

    led_onoff(green, False)
    print("Waiting for 0.2 sec before reset...")
    utime.sleep_ms(200)
    machine.reset()

    pn.close_sockets(serv_sock_text, serv_sock_crypto, conn_text, conn_crypto)
    if uart:
        uart.deinit()

    led_onoff(green, False)
    print("Waiting for 0.2 sec before reset...")
    utime.sleep_ms(200)
    machine.reset()




def run_hybrid_server_sync2(uart, fixed_binary_key, settings):
    if settings['ip']:
        serv_sock_text, serv_sock_crypto, tcp_poller = pn.init_server_sockets_async(settings, settings[utils.MY_IP], utils.TEXT_PORT, utils.ENC_PORT)
        conn_text, conn_crypto = None, None

    tcp_polled = None
    while True:
        await uasyncio.sleep_ms(pn.ASYNC_SLEEP_MS)
        if settings['ip']:
            tcp_polled = tcp_poller.poll(0)
        if not tcp_polled:
            #if uart.any():
            await process_serial_msg(uart, fixed_binary_key, settings)
            #gc_start_time = utils.garbage_collect(gc_start_time)
        else:
            print('tcp_polled[0][0]: ', tcp_polled[0][0])
            if serv_sock_text:
                if tcp_polled[0][0] == serv_sock_text:
                    print('pc is connecting...')
                    conn_text, addr, tcp_poller = pn.init_connection_async(serv_sock_text, tcp_poller)
                elif tcp_polled[0][0] == conn_text:
                    print('data available from PC...')
                    b64 = conn_text.recv(128)
                    if b64:
                        process_tcp_msg(b64, encrypt_text, settings[utils.CHANNEL], uart, settings['peer_ip'], utils.ENC_PORT, fixed_binary_key)
                    else:
                        conn_text = pn.close_server_socket(conn_text, tcp_poller)
            elif tcp_polled[0][0] == serv_sock_crypto:
                print('peer is connecting...')
                conn_crypto, addr, tcp_poller = pn.init_connection_async(serv_sock_crypto, tcp_poller)
            elif tcp_polled[0][0] == conn_crypto:
                print('data available from peer...')
                b64 = conn_crypto.recv(128)
                print('\n### tcp data received: ', b64, '\n')
                if b64:
                    process_tcp_msg(b64, decrypt_crypto, settings[utils.CHANNEL], uart, settings['host_ip'], settings['host_port'], fixed_binary_key)
                else:
                    conn_crypto = pn.close_server_socket(conn_crypto, tcp_poller)

    pn.close_sockets(serv_sock_text, serv_sock_crypto, conn_text, conn_crypto)
    if uart:
        uart.deinit()

    led_onoff(green, False)
    print("Waiting for 0.2 sec before reset...")
    utime.sleep_ms(200)
    machine.reset()

def run_hybrid_server_sync_old(uart, fixed_binary_key, settings):
    global gc_start_time
    gc_start_time = utime.ticks_ms()

    if settings['ip']:
        serv_sock_text, serv_sock_crypto, text_vpoller, crypto_vpoller = pn.init_server_sockets(settings, settings[utils.MY_IP], utils.TEXT_PORT, utils.ENC_PORT)
        conn_text, conn_crypto, text_cpoller, crypto_cpoller = None, None, None, None

    tcp_polled = None
    while True:
        #await uasyncio.sleep_ms(pn.ASYNC_SLEEP_MS)
        if settings['ip']:
            text_vpolled = None if text_vpoller is None else text_vpoller.poll(0)
            text_cpolled = None if text_cpoller is None else text_cpoller.poll(0)
            crypto_vpolled = None if crypto_vpoller is None else crypto_vpoller.poll(0)
            crypto_cpolled = None if crypto_cpoller is None else crypto_cpoller.poll(0)
        if not (text_vpolled or crypto_vpolled or text_cpolled or crypto_cpolled):
            #if uart.any():
            process_serial_msg_sync(uart, fixed_binary_key, settings)
            #gc_start_time = utils.garbage_collect(gc_start_time)
        else:
            print(f'text_vp:{text_vpolled} text_cp:{text_cpolled} crypto_vp:{crypto_vpolled} crypto_cp:{crypto_cpolled}')
            if serv_sock_text:
                if text_vpolled:
                    print('text_vpoller: pc is connecting...')
                    conn_text, addr, text_cpoller = pn.init_connection(serv_sock_text, text_cpoller)
                    text_vpolled = None
                elif text_cpolled:
                    print('text_cpoller: data available from PC...')
                    b64 = conn_text.recv(128)
                    if b64:
                        process_tcp_msg(b64, encrypt_text, settings[utils.CHANNEL], uart, settings['peer_ip'], utils.ENC_PORT, fixed_binary_key)
                    else:
                        conn_text = pn.close_server_socket(conn_text, text_cpoller)
                    text_cpolled = None
            elif crypto_vpolled:
                print('crypto_vpoller: peer is connecting...')
                conn_crypto, addr, crypto_cpoller = pn.init_connection(serv_sock_crypto, crypto_cpoller)
                crypto_vpolled = None
            elif crypto_cpolled:
                print('crypto_cpoller: data available from peer...')
                b64 = conn_crypto.recv(128)
                print('\n### tcp data received: ', b64, '\n')
                if b64:
                    process_tcp_msg(b64, decrypt_crypto, settings[utils.CHANNEL], uart, settings['host_ip'], settings['host_port'], fixed_binary_key)
                else:
                    conn_crypto = pn.close_server_socket(conn_crypto, crypto_cpoller)
                crypto_cpolled = None

    pn.close_sockets(serv_sock_text, serv_sock_crypto, conn_text, conn_crypto)
    if uart:
        uart.deinit()

    led_onoff(green, False)
    print("Waiting for 0.2 sec before reset...")
    utime.sleep_ms(200)
    machine.reset()

async def run_hybrid_server(uart, fixed_binary_key, settings):
    global gc_start_time
    gc_start_time = utime.ticks_ms()

    if settings['ip']:
        serv_sock_text, serv_sock_crypto, tcp_poller = pn.init_server_sockets_async(settings, settings[utils.MY_IP], utils.TEXT_PORT, utils.ENC_PORT)
        conn_text, conn_crypto = None, None

    tcp_polled = None
    while True:
        await uasyncio.sleep_ms(pn.ASYNC_SLEEP_MS)
        if settings['ip']:
            tcp_polled = tcp_poller.poll(0)
        if not tcp_polled:
            #if uart.any():
            await process_serial_msg(uart, fixed_binary_key, settings)
            #gc_start_time = utils.garbage_collect(gc_start_time)
        else:
            print('tcp_polled[0][0]: ', tcp_polled[0][0])
            if serv_sock_text:
                if tcp_polled[0][0] == serv_sock_text:
                    print('pc is connecting...')
                    conn_text, addr, tcp_poller = pn.init_connection_async(serv_sock_text, tcp_poller)
                elif tcp_polled[0][0] == conn_text:
                    print('data available from PC...')
                    b64 = conn_text.recv(128)
                    if b64:
                        process_tcp_msg(b64, encrypt_text, settings[utils.CHANNEL], uart, settings['peer_ip'], utils.ENC_PORT, fixed_binary_key)
                    else:
                        conn_text = pn.close_server_socket(conn_text, tcp_poller)
            elif tcp_polled[0][0] == serv_sock_crypto:
                print('peer is connecting...')
                conn_crypto, addr, tcp_poller = pn.init_connection_async(serv_sock_crypto, tcp_poller)
            elif tcp_polled[0][0] == conn_crypto:
                print('data available from peer...')
                b64 = conn_crypto.recv(128)
                print('\n### tcp data received: ', b64, '\n')
                if b64:
                    process_tcp_msg(b64, decrypt_crypto, settings[utils.CHANNEL], uart, settings['host_ip'], settings['host_port'], fixed_binary_key)
                else:
                    conn_crypto = pn.close_server_socket(conn_crypto, tcp_poller)

    pn.close_sockets(serv_sock_text, serv_sock_crypto, conn_text, conn_crypto)
    if uart:
        uart.deinit()

    led_onoff(green, False)
    print("Waiting for 0.2 sec before reset...")
    utime.sleep_ms(200)
    machine.reset()

def main():
    led_start()
    utime.sleep_ms(1000)
    settings = utils.load_settings()
    print(settings)

    uart, settings = pn.init_connections(settings)

    fixed_binary_key = coder.fix_len_and_encode_key(settings['key'])

    if settings[utils.CONFIG]:
        led_state_setting()
        loop = uasyncio.get_event_loop()
        if settings['ip']:
            cw.prepare_web()
            loop.create_task(uasyncio.start_server(cw.server._handle_request, '0.0.0.0', 80))
        loop.create_task(run_serial_config_server(uart, settings))
    else:
        #loop = uasyncio.get_event_loop()
        if settings['channel']==1:
            #loop.create_task(run_tcp_server(uart, fixed_binary_key, settings))
            run_tcp_server_sync(uart, fixed_binary_key, settings)
        else:
            #loop.create_task(run_hybrid_server(uart, fixed_binary_key, settings))
            run_hybrid_server_sync(uart, fixed_binary_key, settings)

    loop.run_forever()

if __name__ == '__main__':
    main()
