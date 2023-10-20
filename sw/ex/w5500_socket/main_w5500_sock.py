'''
W5500 
'''
import machine
import utime
from usocket import socket
import uselect

from led import *
import pico_net as pn

led_init()

def run_hybrid_server():
    #net_info = pn.pico_net_init(True, None, None, None) # DHCP
    net_info = pn.pico_net_init(False, '192.168.2.15', '255.255.255.0', '192.168.2.1') # DHCP

    ip, subnet, gateway, dns = net_info
    port = 5005
    print('IP assigned: ', ip)
    led_state_good()

    start_time = utime.ticks_ms()
    sock = socket()
    sock.bind((ip, int(port)))
    print('Listening on socket: ', sock)
    sock.listen(1)
    print('Elapsed time for socket bind & listen: ', utime.ticks_ms() - start_time)

    poller_connection = uselect.poll()
    poller_connection.register(sock, uselect.POLLIN)
    while not poller_connection.poll(100):
        print('Waiting for connection... by poll(100)')

    conn, addr = sock.accept()
    print('Connected by ', conn, ' from ', addr)
    poller_data = uselect.poll()
    poller_data.register(conn, uselect.POLLIN)
    loop=True
    while loop:
        try:
            if not poller_data.poll(100):
                print('polling... no data available')
                continue
            else:
                print('data available')
                data = conn.recv(128)
                print('received data: ', data)
                if not data:
                    print('Empty data received. break')
                    break
                conn.send(f'{data} received')
        except OSError as e:
            print('OSError: ', e)
            loop=False
            break

    sock.close()
    if conn:
        conn.close()

    utime.sleep(2)
    return

def main_single():
    led_start()
    run_hybrid_server()

    machine.reset()

if __name__ == '__main__':
    main_single()