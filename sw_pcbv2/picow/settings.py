'''settings
store password to database
https://www.vaadata.com/blog/how-to-securely-store-passwords-in-database/
'''
import ujson

KEY = 'key'
BAUD = 'baud'
PARITY = 'parity'
DATASIZE = 'data_size'
STOPBITS = 'stopbits'

DHCP = 'dhcp'
IP = 'ip'
GATEWAY = 'gateway'
SUBNETMASK = 'subnet_mask'
PORT = 'port'

PEERIP = 'peer_ip'
PEERPORT = 'peer_port'

default_settings = {
    KEY:'00000000',
    BAUD : 9600,
    PARITY : None,
    DATASIZE : 8,
    STOPBITS : 1,
    DHCP : True,
    IP : '192.168.0.256',
    GATEWAY : '192.168.0.1',
    SUBNETMASK : '255.255.255.0',
    PORT : 5002,
    PEERIP : '192.168.0.256',
    PEERPORT : 5002
}

SETTING_FILE = 'settings.json'

def init_settings():
    #create a new file called 'settings.json' truncating the old one if it exists
    #and write the default settings to it
    f = open(SETTING_FILE, 'w', encoding='utf-8')
    f.write(ujson.dumps(default_settings))
    f.close()

# write a function that update a single setting
def update_setting(key, value):
    #read the settings file
    f = open(SETTING_FILE, 'r', encoding='utf-8')
    settings = ujson.loads(f.read())
    f.close()
    #update the setting
    settings[key] = value
    #write the settings file
    f = open(SETTING_FILE, 'w', encoding='utf-8')
    f.write(ujson.dumps(settings))
    f.close()

# write a function that returns a single setting
def get_setting(key):
    #read the settings file
    f = open(SETTING_FILE, 'r', encoding='utf-8')
    settings = ujson.loads(f.read())
    f.close()
    #return the setting
    return settings[key]

