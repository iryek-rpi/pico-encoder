'''
W5500 
'''
import machine
from machine import Pin
from machine import UART
import utime
import gc
import ujson
import mpyaes as aes
import coder
from led import *
import utils
import pico_net as pn

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

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=BAUD_RATE, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)
    return uart0

def process_serial_msg(uart):
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
            else:
                print('Unknown command')
        except Exception as e:
            print(e)
        
    print('.', end='')

    return

def process_tcp_msg(conn, fixed_binary_key):
    b64 = conn.recv(128)
    print('data received: ', b64)
    print('type(b64): ', type(b64))
    
    if len(b64) <= 4:
        print('irregular data. Exit')
        return None
    else:
        cmd, msg = b64[:4], b64[4:]
        cmd = cmd.decode('utf-8')
        print(f'cmd: {cmd}')

        if cmd == 'TEXT':
            print('msg: ', msg)
            IV = aes.generate_IV(16)
            cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
            msg = cipher.encrypt(msg)
            iv_c = IV + msg
            print('IV: ', IV, ' msg: ', msg)
            conn.send(iv_c)
        elif cmd == 'CIPH':
            print('msg: ', msg)
            IV, msg = msg[:16], msg[16:]
            print('IV: ', IV, ' msg: ', msg)
            msga = bytearray(msg)
            cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
            plaintext = cipher.decrypt(msga)
            conn.send(plaintext)

        return msg

def process_tcp_text(b64 fixed_binary_key):
    print('data received: ', b64)
    print('type(b64): ', type(b64))
    
    if len(b64) <= 4:
        print('irregular data. Exit')
        return None
    else:
        print('msg: ', b64)
        IV = aes.generate_IV(16)
        cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
        msg = cipher.encrypt(b64)
        print('IV:', IV, ' msg:', msg)
        return IV + msg

def process_tcp_crypto(b64, fixed_binary_key):
    print('data received: ', b64)
    print('type(b64): ', type(b64))
    
    if len(b64) <= 4:
        print('irregular data. Exit')
        return None
    else:
        print('b64: ', b64)
        IV, msg = b64[:16], b64[16:]
        print('IV:', IV, ' msg:', msg)
        msg_ba = bytearray(msg)
        cipher = aes.new(fixed_binary_key, aes.MODE_CBC, IV)
        return cipher.decrypt(msg_ba)

def process_tcp_msg(conn, handler, dest_ip, dest_port, poller):
    b64 = conn.recv(128)
    if b64:
        processed_msg = handler(b64, fixed_binary_key)
        pn.send_data(processed_msg, dest_ip, dest_port)
    else:
        print('Empty data received. Close connection')
        conn.close()
        poller.unregister(conn)
        return None
    
    return conn

def run_hybrid_server(settings, uart, fixed_binary_key):
    global global_run_flag  # reset button flag
    global gc_start_time

    ip, port, crypto_port = settings['ip'], settings['port'], 6005 #settings['crypto_port']
    peer_ip, peer_port = settings['peer_ip'], settings['peer_port']
    host_ip, host_port = settings['host_ip'], settings['host_port']

    gc_start_time = utime.ticks_ms()
    serv_sock_text, serv_sock_crypto, tcp_poller = pn.init_server_sockets(ip, port, crypto_port)
    conn_text, conn_crypto = None, None

    while global_run_flag:
        tcp_polled = tcp_poller.poll(50)
        if not tcp_polled:
            process_serial_msg(uart)
            garbage_collect()
        else:
            if tcp_polled[0][0] == serv_sock_text:
                print('pc is connecting...')
                conn_text, addr, tcp_poller = pn.init_connection(serv_sock_text, tcp_poller)
            elif tcp_polled[0][0] == serv_sock_crypto:
                print('peer is connecting...')
                conn_crypto, addr, tcp_poller = pn.init_connection(serv_sock_crypto, tcp_poller)
            elif tcp_polled[0][0] == conn_text:
                print('data available from PC...')
                conn_text = process_tcp_msg(conn_text, process_tcp_text, peer_ip, peer_port, tcp_poller)
            elif tcp_polled[0][0] == conn_crypto:
                print('data available from peer...')
                conn_crypto = process_tcp_msg(conn_crypto, process_tcp_crypto, host_ip, host_port, tcp_poller)

    pn.close_sockets(serv_sock_text, serv_sock_crypto, conn_text, conn_crypto)
    if uart:
        uart.deinit()

    utime.sleep(2)
    #machine.reset()
    return

def run_serial_server(uart, fixed_binary_key):
    global global_run_flag  # reset button flag
    global gc_start_time

    gc_start_time = utime.ticks_ms()

    while global_run_flag:
        process_serial_msg(uart)
        garbage_collect()
        continue

    if uart:
        uart.deinit()

    utime.sleep(2)

    return

def main_single():
    global global_run_flag

    led_start()
    settings = utils.load_json_settings()
    print(settings)

    fixed_binary_key = coder.fix_len_and_encode_key(settings['key'])

    global_run_flag = True
    uart = init_serial()
    net_info = pn.init_ip(settings['dhcp'], settings['ip'], settings['subnet'], settings['gateway'])

    if net_info and net_info[0]:
        led_state_good()
        print('IP assigned: ', net_info[0])
        settings['ip'], settings['subnet'], settings['gateway'] = net_info[0], net_info[1], net_info[2]
        utils.save_settings(ujson.dumps(settings))
        run_hybrid_server(settings, uart, fixed_binary_key)
    else:
        print('No IP assigned')
        led_state_no_ip()
        run_serial_server(uart, fixed_binary_key)

    led_onoff(green, False)
    print("Waiting for 2 sec")
    utime.sleep(2)
    print("Exit from main function")

    machine.reset()

if __name__ == '__main__':
    main_single()