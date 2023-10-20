import utime
from usocket import socket
import uselect

import pico_net as pn

if __name__ == '__main__':
    #net_info = pn.pico_net_init(True, None, None, None) # DHCP
    net_info = pn.pico_net_init(False, '192.168.2.15', '255.255.255.0', '192.168.2.1')
    ip, subnet, gateway, dns = net_info
    port = 5005
    print('IP assigned: ', ip)

    start_time = utime.ticks_ms()
    sock = socket()
    sock.bind((ip, int(port)))
    print('Listening on socket: ', sock)
    sock.listen(1)
    print('Elapsed time for socket bind & listen: ', utime.ticks_ms() - start_time)

    #poller_connection = uselect.poll()
    #poller_connection.register(sock, uselect.POLLIN)
    #while not poller_connection.poll(100):
    #    print('Waiting for connection... by poll(100)')

    while True:
        try:
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
                    print('Innter OSError: ', e)
                    loop=False
                    break
        except OSError as e:
            print('Outer OSError: ', e)
            break
