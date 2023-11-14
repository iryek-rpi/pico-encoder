from machine import UART, Pin
import ujson as json

# dump(obj, stream)
#   Serialise obj to a JSON string, writing it to the given stream
# dumps(obj)
#   Return obj represented as a JSON string.

# load(stream)
#   Parse the given stream, interpreting it as a JSON string and deserialising the data to a Python object. The resulting object is returned.
#   Parsing continues until end-of-file is encountered. A ValueError is raised if the data in stream is not correctly formed.
# loads(str)
#   Parse the JSON str and return an object. Raises ValueError if the string is not correctly formed.

def init_serial():
    uart0 = UART(0, tx=Pin(0), rx=Pin(1))
    uart0.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=50)
    return uart0

SETTING_FILE = 'settings2.json'

def load_settings():
    '''returns a dictionary of settings'''
    f = open(SETTING_FILE, 'r', encoding='utf-8')
    settings = json.load(f)
    f.close()
    return settings # return a dictionary

def save_settings(settings):
    '''
    settings is a dictionary
    '''
    #save the settings to the file
    f = open(SETTING_FILE, 'w', encoding='utf-8')
    json.dump(settings, f, indent=4)
    f.close()

def save_str_settings(str_settings):
    #save the settings to the file
    json_settings = json.loads(str_settings)
    save_settings(json_settings)

def main():
    uart = init_serial()
    while True:
        if uart.any():
            str_settings = uart.readline()
            print(str_settings)
            save_str_settings(str_settings)
            break

#if __name__ == '__main__':
#    main()