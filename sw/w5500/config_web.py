from machine import Pin
import machine
import os
import utime as time

from phew import logging, server
from phew.template import render_template
import utils
import constants as c
from main import g_settings

web_settings = None

PHEW_TEMPLATE_PATH = "phew_templates"

def index(request):
    return render_template(f"{PHEW_TEMPLATE_PATH}/index.html", ns=web_settings)

def configure(request):
    current_settings = utils.load_settings()
    print(f"Previous settings in configure: {current_settings}")

    print(request.form)
    
    settings = request.form #ujson.loads(request.form)
    print(settings)
    ns, msg = utils.validate_settings(settings)
    with open("./phew_templates/msg.html", "w") as f:
        f.write(msg)
        f.close()
    if not ns:
        return render_template(f"{PHEW_TEMPLATE_PATH}/index.html", ns=settings)
    else:
        utils.save_settings(ns)
        time.sleep_ms(100)
        machine.reset()
        return render_template(f"{PHEW_TEMPLATE_PATH}/index.html", ns=ns)
    
def app_catch_all(request):
    return "Not found.", 404

def prepare_web():
    try:
        os.remove('./phew_templates/msg.html')
    except:
        pass
    server.add_route("/", handler = index, methods = ["GET"])
    server.add_route("/configure", handler = configure, methods = ["POST"])
    server.set_callback(app_catch_all)

print('Starting web_config script')
    