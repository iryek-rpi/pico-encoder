'''
W5500 
'''
import machine
from machine import Pin
from machine import UART
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

ASYNC_SLEEP_MS = pn.ASYNC_SLEEP_MS

BAUD_RATE = 9600  #19200
if BAUD_RATE == 9600:
    SERIAL1_TIMEOUT = 200 # ms
else:
    SERIAL1_TIMEOUT = 100 # ms

print('Starting W5500 script')
led_init()
btn = Pin(9, Pin.IN, Pin.PULL_UP)
global_run_flag = False
gc_start_time = utime.ticks_ms()

def garbage_collect():
    global gc_start_time

    return 
    time_now = utime.ticks_ms()
    runtime = utime.ticks_diff(time_now, gc_start_time)
    print('===== gc.mem_free(): ', gc.mem_free(), ' at ', runtime)
    if runtime > 500_000:
        gc.collect()
        gc_start_time = time_now
        print('+++++ gc.mem_free(): ', gc.mem_free())

def btn_callback(btn):
    global global_run_flag
    led_onoff(yellow, True)
    led_onoff(green, False)
    print('Button pressed')
    global_run_flag = False

btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_callback)

def init_serial(baud=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT):
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=BAUD_RATE, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)
    return uart0

async def process_serial_msg(uart, fixed_binary_key, settings):
    global global_run_flag
    sm = uart.readline()
    if sm:
        try:
            sm = sm.decode('utf-8')
            sm = sm.strip()
            print(sm)
            cmd = sm[:7]
            print(f'cmd: {cmd}')
            print(f'sm[-7:]: {sm[-7:]}')
            if cmd=='CNF_REQ':
                saved_settings = utils.load_json_settings()
                print('saved_settings: ', saved_settings)
                print('type(saved_settings): ', type(saved_settings))
                str_settings = ujson.dumps(saved_settings)
                print(len(str_settings), ' bytes : ', str_settings)
                msg = bytes('CNF_JSN', 'utf-8') + bytes(str_settings, 'utf-8') + bytes('CNF_END\n', 'utf-8')
                uart.write(msg)
            elif cmd=='CNF_WRT' and sm[-7:]=='CNF_END':
                uart.deinit()
                uart = None
                received_settings = sm[7:-7]
                print(f'Received settings: {received_settings}')
                utils.save_settings(received_settings)
                global_run_flag = False
                return
            elif cmd=='TXT_WRT' and sm[-7:]=='TXT_END':
                received_msg = f'{sm[7:-7]}'
                received_msg = bytes(received_msg.strip(), 'utf-8')
                print(f'TXT_WRT Received msg: {received_msg}')
                encoded_msg = encrypt_text(received_msg, fixed_binary_key)
                if not encoded_msg:
                    print('Encryption result Empty')
                    encoded_msg = bytes('***BAD DATA***', 'utf-8')
                pn.send_data_sync(encoded_msg, settings['peer_ip'], utils.ENC_PORT)
                return
            else:
                print('Unknown command')
        except Exception as e:
            print(e)
        
    print('.', end='')

    return

def encrypt_text(b64, fixed_binary_key):
    print('data received: ', b64)
    print('type(b64): ', type(b64))
    
    #if len(b64) <= 4:
    #    print('irregular data. Exit')
    #    return None
    #else:
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
    
    #if len(b64) <= 4:
    #    print('irregular data. Exit')
    #    return None
    #else:
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

async def run_hybrid_server(settings, uart, fixed_binary_key):
    global global_run_flag  # reset button flag
    global gc_start_time

    gc_start_time = utime.ticks_ms()
    serv_sock_text, serv_sock_crypto, tcp_poller = pn.init_server_sockets(settings, settings[utils.MY_IP], utils.TEXT_PORT, utils.ENC_PORT)
    conn_text, conn_crypto = None, None

    while global_run_flag:
        tcp_polled = tcp_poller.poll(0)
        if not tcp_polled:
            await process_serial_msg(uart, fixed_binary_key, settings)
            garbage_collect()
            #await uasyncio.sleep_ms(ASYNC_SLEEP_MS)
        else:
            print('tcp_polled[0][0]: ', tcp_polled[0][0])
            print('serv_sock_text: ', serv_sock_text)
            print('conn_text: ', conn_text)
            print('serv_sock_crypto: ', serv_sock_crypto)
            print('conn_crypto: ', conn_crypto)
            if serv_sock_text:
                if tcp_polled[0][0] == serv_sock_text:
                    print('pc is connecting...')
                    conn_text, addr, tcp_poller = pn.init_connection(serv_sock_text, tcp_poller)
                elif tcp_polled[0][0] == conn_text:
                    print('data available from PC...')
                    b64 = conn_text.recv(128)
                    if b64:
                        process_tcp_msg(b64, encrypt_text, settings[utils.CHANNEL], uart, settings['peer_ip'], utils.ENC_PORT, fixed_binary_key)
                    else:
                        conn_text = pn.close_server_socket(conn_text, tcp_poller)
            elif tcp_polled[0][0] == serv_sock_crypto:
                print('peer is connecting...')
                conn_crypto, addr, tcp_poller = pn.init_connection(serv_sock_crypto, tcp_poller)
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

    utime.sleep_ms(2000)
    #machine.reset()
    return

async def run_serial_server(uart, fixed_binary_key):
    global global_run_flag  # reset button flag
    global gc_start_time

    gc_start_time = utime.ticks_ms()

    while global_run_flag:
        process_serial_msg(uart)
        await uasyncio.sleep_ms(ASYNC_SLEEP_MS)
        garbage_collect()
        continue

    if uart:
        uart.deinit()

    utime.sleep_ms(100)

    return

async def main_single(net_info, uart, fixed_binary_key, settings):
    global global_run_flag

    if net_info and net_info[0]:
        led_state_good()
        print('IP assigned: ', net_info[0])
        settings['ip'], settings['subnet'], settings['gateway'] = net_info[0], net_info[1], net_info[2]
        utils.save_settings(ujson.dumps(settings))
        await run_hybrid_server(settings, uart, fixed_binary_key)
    else:
        print('No IP assigned')
        led_state_no_ip()
        await run_serial_server(uart, fixed_binary_key)

    led_onoff(green, False)
    print("Waiting for 0.2 sec before reset")
    utime.sleep_ms(200)
    print("Resetting...")

    machine.reset()

def main():
    global global_run_flag

    led_start()
    utime.sleep_ms(1000)
    settings = utils.load_json_settings()
    print(settings)

    fixed_binary_key = coder.fix_len_and_encode_key(settings['key'])
    print('fixed_binary_key: ', fixed_binary_key)

    global_run_flag = True
    uart = init_serial(baud=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)
    net_info = pn.init_ip(settings['ip'], settings['subnet'], settings['gateway'])

    cw.prepare_web()
    loop = uasyncio.get_event_loop()
    loop.create_task(main_single(net_info, uart, fixed_binary_key, settings))
    loop.create_task(uasyncio.start_server(cw.server._handle_request, '0.0.0.0', 80))
    loop.run_forever()


if __name__ == '__main__':
    main()
