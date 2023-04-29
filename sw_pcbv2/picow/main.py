'''pico-w'''
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

SERIAL1_TIMEOUT = 20 # ms
UART1_DELAY = 0.05 # 50ms

led = Pin('LED', Pin.OUT)

interrupt_flag = 0

def callback(btn):
    global interrupt_flag
    interrupt_flag=1

    ap = access_point("위너스 핫스팟")
    ip = ap.ifconfig()[0] # Grab the IP address and store it
    logging.info(f"starting DNS server on {ip}")
    dns.run_catchall(ip)  # Catch all requests and reroute them
    server.run()          # Run the server
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
    uart1.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=SERIAL1_TIMEOUT)

    return uart1

def send_settings(sp, json_settings):
    len_json = bytes(f'{len(json_settings)}\n', 'utf-8')
    print(len_json)

    while True:
        got_ready = False
        while True:
            srecv = sp.readline()
            print(srecv)
            if srecv is None and got_ready:
                break
            try:
                ready = srecv.decode('utf-8')
                if ready=='READY_1\n':
                    got_ready = True
            except Exception as e:
                print(e)

        print('PEER READY_1')
        
        sp.write(len_json)
        utime.sleep(UART1_DELAY)

        restart = True
        got_ready = False
        while True:
            srecv = sp.readline()
            print(srecv)
            if srecv is None and got_ready:
                restart = False
                break
            try:
                ready = srecv.decode('utf-8')
                if ready=='READY_2\n':
                    got_ready = True
                elif ready=='RESTART\n':
                    restart = True
                    break
            except Exception as e:
                print(e)

        if restart:
            continue

        print('PEER READY2')

        nw = sp.write(json_settings)
        print(f'written: {nw}')
        break
    
def main():
    led.on()
    s1 = init_serial()
    json_settings = utils.load_json_settings()
    print(json_settings)

    send_settings(s1, json_settings)
    led.on()

    callback2(0)

    return

if __name__ == "__main__":
    main()