import logging
import json
from w5500.utils import DEFAUlT_SETTINGS
from w5500 import constants as c

SETTING_FILE = 'pc_settings.json'
DEFAULT_SERIAL_PORT = 'COM6'

logger = logging.getLogger('winc')

def init_settings():
    #create a new file truncating the old one if it exists
    #and write the default settings to it
    DEFAUlT_SETTINGS[c.SERIAL_PORT] = DEFAULT_SERIAL_PORT
    return save_settings(DEFAUlT_SETTINGS)

def load_settings():
    try:
        with open(SETTING_FILE, 'r', encoding='utf-8') as f
           return json.load(f)
    except OSError:
        return init_settings()

def save_settings(settings):
    try:
        with open(SETTING_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f)
            return settings
    except OSError as e:
        logger.debug(f'설정 저장 오류: {e}')
        return None

def read_device_options(self):
    global global_serial_device
    global global_serial_sending

    self.comm_port = self.entry_serial_port.get()
    while global_serial_device:
        time.sleep(0.02)

    try:
        global_serial_sending = True
        global_serial_device = serial.Serial(port=self.comm_port, baudrate=BAUD_RATE, bytesize=8, parity='N', stopbits=1, timeout=SERIAL1_TIMEOUT, write_timeout=SERIAL1_TIMEOUT) 
        self.add_status_msg(f"시리얼 연결됨: COM 포트({self.comm_port}) 속도:{BAUD_RATE}bps 데이터:{8}bit 패리티:{'N'} 정지:{1}bit")
    except serial.serialutil.SerialException as e:
        #CTkMessagebox(title="Info", message=f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        self.add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        logging.debug('시리얼 예외 발생: ', e)
    else:
        global_serial_device.write('CNF_REQ\n'.encode())
        msg = global_serial_device.readline()

        if msg:
            logging.debug(f'수신: {msg}')
            msg = msg.decode('utf-8')
            msg = msg.strip()
            logging.debug(f'수신 decoded: {msg}')
            if msg.startswith('CNF_JSN') and msg.endswith('CNF_END'):
                msg = msg[7:-7]
                options = json.loads(msg)
                options['comm'] = self.comm_port
                self.apply_ui_options(options)
                self.add_status_msg(f'수신: {msg}')
                logging.debug(f'수신: {msg}')
                global_serial_device.reset_input_buffer()
            else:
                self.add_status_msg(f'Partial msg received: {msg}')
        else:
            logging.debug('수신: No Data')
            #CTkMessagebox(title="Info", message=f"단말에서 정보를 읽어올 수 없습니다.")
            self.add_status_msg(f"단말에서 정보를 읽어올 수 없습니다. msg:{msg}")

    finally:
        if global_serial_device:
            global_serial_device.close()
            global_serial_device = None
        global_serial_sending = False

def write_device_options(self):
    global global_serial_device
    global global_serial_sending

    self.comm_port = self.entry_serial_port.get()
    while global_serial_device:
        time.sleep(0.02)

    try:
        global_serial_sending = True
        global_serial_device = serial.Serial(port=self.comm_port, baudrate=BAUD_RATE, bytesize=8, parity='N', stopbits=1, timeout=SERIAL1_TIMEOUT, write_timeout=SERIAL1_TIMEOUT) 
        self.add_status_msg(f"시리얼 연결됨: COM 포트({self.comm_port}) 속도:{BAUD_RATE}bps 데이터:{8}bit 패리티:{'N'} 정지:{1}bit")
    except serial.serialutil.SerialException as e:
        #CTkMessagebox(title="Info", message=f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        self.add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        logging.debug('시리얼 예외 발생: ', e)
    else:
        options = self.read_ui_options()
        options.pop('comm')
        str_options = json.dumps(options)

        msg = bytes(f"CNF_WRT{str_options}CNF_END\n", encoding='utf-8')
        written=global_serial_device.write(msg)
        logging.debug(f'송신: {msg}')
        logging.debug(f'송신: {written} bytes')
        self.add_status_msg(f'디바이스에 설정 송신: {written}bytes => {msg}')
        time.sleep(0.3)
    finally:
        if global_serial_device:
            global_serial_device.close()
            global_serial_device = None
        global_serial_sending = False
