'''settings
store password to database
https://www.vaadata.com/blog/how-to-securely-store-passwords-in-database/
'''
import os
import ujson as json
import constants as c
from constants import DEFAUlT_SETTINGS

#{"speed": "9600", "parity": "N", "data": "8", "stop": "1", "ip": "192.168.0.5", "subnet": "255.255.255.0", "gateway": "192.168.0.1", "port": "8501", "peer_ip": "192.168.0.6", "peer_port": "8502", "host_ip": "192.168.0.2", "host_port": "8503", "key": "12345678"}


SETTING_FILE = 'settings.json'

def get_device_id():
    l = os.listdir()
    try:
        for f in l:
            if f.startswith('mac_'):
                return int(f[4:f.find('.')])
    except Exception as e:
        print(e)

    return 999

def init_settings():
    #create a new file called 'settings.json' truncating the old one if it exists
    #and write the default settings to it
    save_settings(DEFAUlT_SETTINGS)

def load_settings():
    '''returns a dictionary of settings'''
    try:
        f = open(SETTING_FILE, 'r', encoding='utf-8')
    except OSError:
        init_settings()
        f = open(SETTING_FILE, 'r', encoding='utf-8')

    settings = json.load(f)
    f.close()
    return settings # return a dictionary

def save_str_settings(str_settings):
    #save the settings to the file
    f = open(SETTING_FILE, 'w', encoding='utf-8')
    f.write(str_settings) # obj -> json formatted string
    f.close()

def save_settings(settings):
    '''
    settings is a dictionary
    '''
    #save the settings to the file
    f = open(SETTING_FILE, 'w', encoding='utf-8')
    json.dump(settings, f)
    f.close()

def validate_settings(settings):
    #check if the settings are valid
    msg = ''
    ns = settings.copy()
    ns[c.SPEED] = int(settings[c.SPEED])
    #if ns[PARITY] is 'N':
    #    ns[PARITY] = None
    #else:
    #    ns[PARITY] = int(ns[PARITY])

    ns[c.CHANNEL] = int(settings[c.CHANNEL])
    if ns[c.PARITY] != 'N':
        ns[c.PARITY] = int(settings[c.PARITY])
    ns[c.DATA] = int(settings[c.DATA])
    ns[c.STOP] = int(settings[c.STOP])

    if not validate_ip_string(settings[c.MY_IP]):
        msg += f'IP 주소 오류: {settings[c.MY_IP]}<br>'

    if not validate_ip_string(settings[c.GATEWAY]):
        msg += f'게이트웨이 오류: {settings[c.GATEWAY]}<br>'
    
    if not validate_ip_string(settings[c.PEER_IP]):
        msg += f'상대 단말 IP 주소 오류: {settings[c.PEER_IP]}<br>'

    if not validate_ip_string(settings[c.HOST_IP]):
        msg += f'호스트 IP 주소 오류: {settings[c.HOST_IP]}<br>'

    if not validate_port_string(settings[c.HOST_PORT]):
        msg += f'호스트 포트 오류: {settings[c.HOST_PORT]} 1023<포트번호<65536<br>'
    else:
        ns[c.HOST_PORT] = int(settings[c.HOST_PORT])

    if len(ns[c.KEY])>16 or len(ns[c.KEY])<4:
        msg += f'암호키 오류: {settings[c.KEY]} 암호키는 4~16자리로 지정해야 합니다<br>'

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
    settings = json.loads(f.read())
    f.close()
    #update the setting
    settings[key] = value
    #write the settings file
    f = open(SETTING_FILE, 'w', encoding='utf-8')
    f.write(json.dumps(settings))
    f.close()

# write a function that returns a single setting
def get_setting(key):
    settings = load_settings()
    return settings[key]

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

def garbage_collect(start_time):
    return 
    time_now = utime.ticks_ms()
    runtime = utime.ticks_diff(time_now, start_time)
    print('===== gc.mem_free(): ', gc.mem_free(), ' at ', runtime)
    if runtime > 500_000:
        gc.collect()
        print('+++++ gc.mem_free() after gc.collect(): ', gc.mem_free())
        return time_now
    return start_time
