import sys
import time
import logging

import json
import socket
import serial
import customtkinter as ctk
import asyncio

from layout import *
import device_options as do
from crypto_ex import *

TEXT_PORT = 8501
ENC_PORT = 8502

global_serial_device = None
global_serial_sending = False
app = None

# config a logger using default logger
logging.basicConfig(filename='app.log', filemode='w', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

BAUD_RATE = 9600
if BAUD_RATE == 9600:
    SERIAL1_TIMEOUT = 0.2 # sec
else:
    SERIAL1_TIMEOUT = 0.1 # sec

SUBNET_MASK = '255.255.255.0'
COMM_PORT = '/dev/ttyUSB0'
GATEWAY = '192.168.0.1'

ctk.set_appearance_mode("Light")  #"System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

async def handle_client(reader, writer):
    request = None
    while request != 'quit':
        request = (await reader.read(255)).decode('utf8')
        response = str(eval(request)) + '\n'
        writer.write(response.encode('utf8'))
        await writer.drain()
    writer.close()

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        init_ui(self)

    def add_status_msg(self, msg):
        self.clear_status_msg()
        self.errortextbox.configure(state='normal')
        self.errortextbox.insert('0.0', "\n" + msg + "\n")
        self.errortextbox.configure(state='disabled')

    def clear_status_msg(self):
        self.errortextbox.configure(state='normal')
        self.errortextbox.delete("1.0", "end-1c")
        self.errortextbox.configure(state='disabled')

    def limit_key(self, sv):
        content = sv.get()

        if len(content) > 16: 
            #CTkMessagebox(title="알림", message="키는 16자 이내로 입력하세요.", icon="info")
            self.add_status_msg("키는 16자 이내로 입력하세요.")
            sv.set(content[:16])
            return False
        return True

    def read_ui_options(self):
        return do.read_ui_options(self)

    def apply_ui_options(self, options):
        do.apply_ui_options(self, options)

    def read_options_file(self):
        return do.read_options_file()

    def write_options_file(self, options):
        do.write_options_file(options)

    def read_device_option_event(self):
        #options = self.read_ui_options()
        self.read_device_options()
        options = self.read_ui_options()
        self.write_options_file(options)

    def apply_device_option_event(self):
        self.write_device_options()

        options = self.read_ui_options()
        self.write_options_file(options)

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

    def find_host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def get_device_ip(self):
        options = self.read_ui_options()
        return options['ip']

    def clear_errortext_event(self):
        plaintext = self.entry_plaintext.get()
        if not plaintext:
            self.add_status_msg("암호화할 평문(16글자 이내)를 입력하세요")
            return

        if not self.c_socket:
            if not self.init_connection(self.get_device_ip(), TEXT_PORT):
                self.add_status_msg("네트워크 연결에 실패했습니다")
                return

        self.send_plaintext(plaintext)

    def change_cipher_event(self, new_cipher: str):
        self.cipher = new_cipher

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

def main():
    global app
    
    app = App()

    options = app.read_options_file()
    app.apply_ui_options(options)
    app.comm_port = options["comm"]

    app.mainloop()

if __name__ == "__main__":
    main()
