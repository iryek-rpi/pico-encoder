from machine import Pin
from machine import Timer
from machine import UART
import ubinascii

import utime

from phew import logging, server, access_point, dns
from phew.template import render_template
from phew.server import redirect

import utils

DOMAIN = "Winners.hotspot"  # This is the address that is shown on the Captive Portal

SERIAL_TIMEOUT = 100 # ms

led = Pin('LED', Pin.OUT)

def callback2(btn):
    global interrupt_flag
    interrupt_flag=1
    # Set to Accesspoint mode
    # Change this to whatever Wifi SSID you wish
    ap = access_point("위너스 핫스팟")
    ip = ap.ifconfig()[0]
    # Grab the IP address and store it
    #logging.info(f"starting DNS server on {ip}")
    # # Catch all requests and reroute them
    dns.run_catchall(ip)
    server.run()                            # Run the server
    logging.info("Webserver Started")    

print('Starting script')

@server.route("/", methods=['GET'])
def index(request):
    """ Render the Index page"""
    if request.method == 'GET':
        logging.debug("Get request")
        return render_template("index.html")

# microsoft windows redirects
@server.route("/ncsi.txt", methods=["GET"])
def hotspot(request):
    print(request)
    print("ncsi.txt")
    return "", 200


@server.route("/connecttest.txt", methods=["GET"])
def hotspot(request):
    print(request)
    print("connecttest.txt")
    return "", 200


@server.route("/redirect", methods=["GET"])
def hotspot(request):
    print(request)
    print("****************ms redir*********************")
    return redirect(f"http://{DOMAIN}/", 302)

# android redirects
@server.route("/generate_204", methods=["GET"])
def hotspot(request):
    print(request)
    print("******generate_204********")
    return redirect(f"http://{DOMAIN}/", 302)

# apple redir
@server.route("/hotspot-detect.html", methods=["GET"])
def hotspot(request):
    print(request)
    """ Redirect to the Index Page """
    return render_template("index.html")


@server.catchall()
def catch_all(request):
    print("***************CATCHALL***********************\n" + str(request))
    return redirect("http://" + DOMAIN + "/")

def init_serial():
    uart1 = UART(1, tx=Pin(4), rx=Pin(5))
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL_TIMEOUT)

    return uart1

def main():    
    s1 = init_serial()
    json_settings = utils.load_json_settings()
    len_json = len(json_settings)
    print(f'len_json: {len_json}')
    s1.write(f'{len_json}\n')
    nw = s1.write(json_settings)
    print(f'written: {nw}')

    led.on()

    return

if __name__ == "__main__":
    main()


'''
    ap = access_point("위너스 핫스팟")
    ip = ap.ifconfig()[0]   # Grab the IP address and store it
    logging.info(f"starting DNS server on {ip}")
    # # Catch all requests and reroute them
    dns.run_catchall(ip)
    server.run()                            # Run the server
    logging.info("Webserver Started")



    buf2eth = b''
    buf2pc = b''

    while True:
        data2eth = spc.read()
        if data2eth:
            led_blink_red()
            print(buf2eth)
            buf2eth += data2eth
            print(buf2eth)
        else:
            if buf2eth:
                buf2eth = ubinascii.hexlify(buf2eth)
                n_to_write = len(buf2eth)
                #buf2eth = ubinascii.a2b_base64(buf2eth)
                while True:
                    n_written = seth.write(buf2eth)
                    if not n_written:
                        print("Error write to uart1")
                        break
                    elif n_written < n_to_write:
                        buf2eth = buf2eth[n_written:]
                        n_to_write -= n_written
                    else:
                        break
                buf2eth = b''
            else:
                data2pc = seth.read()
                if data2pc:
                    led_blink_red()
                    #print('buf2pc: ', buf2pc)
                    buf2pc += data2pc
                    #print('buf2pc: ', buf2pc)
                else:
                    if buf2pc and not (buf2pc==b'\x00'):
                        print(buf2pc)
                        if not interrupt_flag:
                            buf2pc = ubinascii.unhexlify(buf2pc)                        
                        n_to_write = len(buf2pc)
                        while True:
                            n_written = spc.write(buf2pc)
                            if not n_written:
                                print("Error write to uart0")
                                break
                            elif n_written < n_to_write:
                                buf2pc = buf2pc[n_written:]
                                n_to_write -= n_written
                            else:
                                break
                        buf2pc = b''

    while 0:
        #b64 = conn.recv(1024)
        data = ubinascii.a2b_base64(b64)
        u0.write(b64)
        u0.write(b'\n\n')
        time.sleep(0.1)
        u0.write(data)
        time.sleep(0.1)

        led_blink_green()
        led_blink_red()

def blink_red(t):
    led_red.toggle()

def blink_green(t):
    led_green.toggle()

def led_blink_red():
    timer_red.init(freq=10, mode=Timer.PERIODIC, callback=blink_red)

def led_blink_green():
    timer_red.init(freq=10, mode=Timer.PERIODIC, callback=blink_green)

def led_on_red():
    timer_red.deinit()
    led_red.on()

def led_on_green():
    timer_red.deinit()
    led_green.on()

def led_off_red():
    timer_red.deinit()
    led_red.off()

def led_off_green():
    timer_red.deinit()
    led_green.off()

if __name__ == '__main__':
    main()
'''