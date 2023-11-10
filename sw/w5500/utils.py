'''settings
store password to database
https://www.vaadata.com/blog/how-to-securely-store-passwords-in-database/
'''
import os
import ujson

CH_TCP = 1      # channel to host
CH_SERIAL = 0

TEXT_PORT = 8501
ENC_PORT = 8502

MODE = 'mode'

BAUD = 'baud'
PARITY = 'parity'
DATASIZE = 'datasize'
STOP = 'stop'

#{"speed": "9600", "parity": "N", "data": "8", "stop": "1", "ip": "192.168.0.5", "subnet": "255.255.255.0", "gateway": "192.168.0.1", "port": "8501", "peer_ip": "192.168.0.6", "peer_port": "8502", "host_ip": "192.168.0.2", "host_port": "8503", "key": "12345678"}

MY_IP = 'ip'
CRYPTO_PORT = 'crypto_port'
GATEWAY = 'gateway'
SUBNET = 'subnet'
PEER_IP = 'peer_ip'
HOST_IP = 'host_ip'
HOST_PORT = 'host_port'
SPEED = 'speed'
PARITY = 'parity'
DATA = 'data'
STOP = 'stop'
CHANNEL = 'channel'
KEY = 'key'

DEFAUlT_SETTINGS = {
    MY_IP : '192.168.1.10',
    CRYPTO_PORT : 8502,
    GATEWAY : '192.168.0.1',
    SUBNET : '255.255.255.0',
    PEER_IP : '192.168.0.5',
    HOST_IP : '192.168.0.6',
    HOST_PORT : 8503,
    SPEED : 9600,
    PARITY : 'N',   #N, E, O
    DATA : 8,
    STOP : 1,
    CHANNEL : CH_TCP, # 0=tcp, 1=serial
    KEY:'12345678'
}

SETTING_FILE = 'settings.json'

def init_settings():
    #create a new file called 'settings.json' truncating the old one if it exists
    #and write the default settings to it
    f = open(SETTING_FILE, 'w', encoding='utf-8')
    f.write(ujson.dumps(DEFAUlT_SETTINGS))
    f.close()


def save_settings(settings):
    #save the settings to the file
    f = open(SETTING_FILE, 'w', encoding='utf-8')
    #f.write(ujson.dumps(settings))
    f.write(settings)
    f.close()

def validate_settings(settings):
    #check if the settings are valid
    msg = ''
    ns = settings.copy()
    ns[BAUD] = int(settings[BAUD])
    if ns[PARITY] is 'no':
        ns[PARITY] = 'no'
    else:
        ns[PARITY] = int(ns[PARITY])

    ns[DATASIZE] = int(settings[DATASIZE])
    ns[STOP] = int(settings[STOP])

    if not validate_ip_string(settings[IP]):
        msg += f'IP 주소 오류: {settings[IP]}<br>'

    if not validate_port_string(settings[PORT]):
        msg += f'포트 번호 오류: {settings[PORT]} 1023<포트번호<65536<br>'
    else:
        ns[PORT] = int(settings[PORT])

    if not validate_ip_string(settings[GATEWAY]):
        msg += f'게이트웨이 오류: {settings[GATEWAY]}<br>'
    
    if not validate_ip_string(settings[PEER_IP]):
        msg += f'상대 단말 IP 주소 오류: {settings[PEER_IP]}<br>'

    if not validate_port_string(settings[PEER_PORT]):
        msg += f'상대 단말 포트 오류: {settings[PEER_PORT]} 1023<포트번호<65536<br>'
    else:
        ns[PEER_PORT] = int(settings[PEER_PORT])

    if not validate_ip_string(settings[HOST_IP]):
        msg += f'호스트 IP 주소 오류: {settings[HOST_IP]}<br>'

    if not validate_port_string(settings[HOST_PORT]):
        msg += f'호스트 포트 오류: {settings[HOST_PORT]} 1023<포트번호<65536<br>'
    else:
        ns[HOST_PORT] = int(settings[HOST_PORT])

    if len(ns[KEY]) != 8:
        msg += f'암호키 오류: {settings[KEY]} 암호키는 8자리로 지정해야 합니다<br>'

    if msg != '':
        msg = f'<p style="color:Tomato;">설정 오류<br>{msg}</p>'
        return None, msg
    else:
        msg = f'<p style="color:Tomato;">설정 완료</p>'
        return ns, msg

def validate_ip_string(ips):
    '''validate ip string'''
    try:
        ip_list = ips.split('.')
        if len(ip_list) != 4:
            return False
        for ip in ip_list:
            if int(ip) > 255:
                return False
    except Exception as e:
        print(e)
        return False

    return True

def validate_port_string(sp):
    '''validate port string'''
    try:
        port = int(sp)
        if port > 65535 or port < 1024:
            raise ValueError
    except ValueError:
        return False
    return True
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
    settings = load_settings()
    return settings[key]

def load_settings():
    try:
        f = open(SETTING_FILE, 'r', encoding='utf-8')
    except OSError:
        init_settings()
        f = open(SETTING_FILE, 'r', encoding='utf-8')

    json_settings = f.read()
    f.close()
    return json_settings

def load_json_settings():
    _settings = load_settings()
    return ujson.loads(_settings)

def file_exists(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) == 0
    except OSError:
        return False    

def folder_exists(foldername):
    try:
        return (os.stat(foldername)[0] & 0x4000) != 0
    except OSError:
        return False    