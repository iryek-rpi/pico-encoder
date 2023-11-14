from machine import Pin
import machine
import os

from phew import logging, server
from phew.template import render_template
import utils
import pico_net as pn

PHEW_TEMPLATE_PATH = "phew_templates"

def index(request):
    current_settings = utils.load_settings()

    print(f"Previous settings in ap_index: {current_settings}")
    print(f"prev_settings['parity']: {current_settings['parity']}")
    return render_template(f"{PHEW_TEMPLATE_PATH}/index.html", ns=current_settings)

def configure(request):
    current_settings = utils.load_json_settings()
    print("Saving user inputs...")
    print(f"Previous settings in ap_configure: {current_settings}")

    print(request.form)
    print(type(request.form))
    
    settings = request.form #ujson.loads(request.form)
    print(settings)
    ns, msg = utils.validate_settings(settings)
    with open("./phew_templates/msg.html", "w") as f:
        f.write(msg)
        f.close()
    if not ns:
        return render_template(f"{PHEW_TEMPLATE_PATH}/index.html", ns=settings)
    else:
        ns[utils.CONFIG] = 0
        utils.save_settings(ns)
        utime.sleep_ms(100)
        machine.reset()
        return render_template(f"{PHEW_TEMPLATE_PATH}/index.html", ns=ns)
    
def prepare_web():
    try:
        os.remove('./phew_templates/msg.html')
    except:
        pass
    server.add_route("/", handler = index, methods = ["GET"])
    server.add_route("/configure", handler = configure, methods = ["POST"])

print('Starting web_config script')
    