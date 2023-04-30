'''pico-w'''
from machine import Pin
from machine import Timer
from machine import UART
import os
import ubinascii

import utime
import ujson

from phew import logging, server, access_point, dns
from phew.template import render_template
from phew.server import redirect

import utils

AP_NAME = "Winners WIFI"
AP_DOMAIN = "winners.net"
AP_TEMPLATE_PATH = "ap_templates"
APP_TEMPLATE_PATH = "app_templates"

SERIAL1_TIMEOUT = 20 # ms
UART1_DELAY = 0.05 # 50ms

led = Pin('LED', Pin.OUT)

interrupt_flag = 0

def callback(btn):
    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0] # Grab the IP address and store it
    logging.info(f"starting DNS server on {ip}")
    dns.run_catchall(ip)  # Catch all requests and reroute them
    server.run()          # Run the server
    logging.info("Webserver Started")    

def setup_mode(prev_settings):
    print("Entering setup mode...")
    print(f"Previous settings: {prev_settings}")
    
    def ap_index(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

        print(f"Previous settings in ap_index: {prev_settings}")
        print(f"prev_settings['dhcp']: {prev_settings['dhcp']}")
        print(f"prev_settings['parity']: {prev_settings['parity']}")
        return render_template(f"{AP_TEMPLATE_PATH}/index.html", ns=prev_settings)

    def ap_configure(request):
        print("Saving user inputs...")
        print(f"Previous settings in ap_configure: {prev_settings}")

        print(request.form)
        settings = ujson.loads(request.form)
        print(settings)
        print(type(request.form))
        print(type(settings))
        ns, msg = utils.validate_settings(settings)
        with open("./app_templates/msg.html", "w") as f:
            f.write(msg)
            f.close()
        if not ns:
            return render_template(f"{AP_TEMPLATE_PATH}/index.html", ns=ns)
        else:
            utils.save_settings(ns)
            return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ns=ns)

        #with open(WIFI_FILE, "w") as f:
        #    print(request.form)
        #    print(ujson.dumps(request.form))
        #    ujson.dump(request.form, f)
        #    f.close()

        # Reboot from new thread after we have responded to the user.
        #_thread.start_new_thread(machine_reset, ())
        #return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ssid = request.form["ssid"])
        
    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

        return "Not found.", 404

    server.add_route("/", handler = ap_index, methods = ["GET"])
    server.add_route("/configure", handler = ap_configure, methods = ["POST"])
    server.set_callback(ap_catch_all)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    logging.info(f"starting DNS server on {ip}")
    dns.run_catchall(ip) # Catch all requests and reroute them

print('Starting PICO-W script')


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

    #send_settings(s1, json_settings)
    led.on()

    try:
        os.remove('./ap_templates/msg.html')
    except:
        pass

    setup_mode(ujson.loads(json_settings))
    server.run()          # Run the server
    logging.info("Webserver Started")    

    return

if __name__ == "__main__":
    main()