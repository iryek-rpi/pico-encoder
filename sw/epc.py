import sys
import time
from threading import Thread
import logging

import json
import serial
import customtkinter as ctk
import socket
import select

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

#BAUD_RATE = 19200
BAUD_RATE = 9600
if BAUD_RATE == 9600:
    SERIAL1_TIMEOUT = 0.2 # sec
else:
    SERIAL1_TIMEOUT = 0.1 # sec

SUBNET_MASK = '255.255.255.0'
COMM_PORT = '/dev/ttyUSB0'
GATEWAY = '192.168.0.1'

ctk.set_appearance_mode(
    "Light")  #"System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(
    "green")  # Themes: "blue" (standard), "green", "dark-blue"

class ReceiveTCPTextThread(Thread):
    global app
    def __init__(self, ip, port):
        super().__init__()

        self.plaintext = None
        self.text_socket = None
        self.ip = ip
        self.port = port
        self.name = 'TCP Text Thread'

    def run(self):
        try:
            self.text_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.text_socket.bind((self.ip, int(self.port)))
            self.text_socket.listen(1)
            while True:
                print('Waiting for tcp connection...', self.ip, self.port)
                conn, addr = self.text_socket.accept()
                print('Connected by ', conn, ' from ', addr)
                while True:
                    print('Waiting for tcp data...')
                    data = conn.recv(1024)
                    if not data:
                        break
                    print('PlainText received through socket: ', data)
                    self.plaintext = data.decode('utf-8')
                    #app.entry_dectext.configure(state='normal')
                    #app.entry_dectext.delete(0, "end")
                    #app.entry_dectext.insert(0, data)
                    #app.entry_dectext.configure(state='disabled')
                    app.add_status_msg(f'복호화 데이터 수신: {data}')
                conn.close()
            
        except Exception as e:
            print('Exception: ', e)

class ReceiveSerialTextThread(Thread):
    def __init__(self):
        super().__init__()

        self.plaintext = None
        self.name = 'Serial Text Thread'

    def run(self):
        global app
        global global_serial_device
        global global_serial_sending
        while True:
            try:
                if not global_serial_sending and not global_serial_device:
                    global_serial_device = serial.Serial(port=app.comm_port, baudrate=BAUD_RATE, bytesize=8, parity='N', stopbits=1, timeout=SERIAL1_TIMEOUT, write_timeout=SERIAL1_TIMEOUT) 
                    app.add_status_msg(f"시리얼 연결됨: COM 포트({app.comm_port}) 속도:{BAUD_RATE}bps 데이터:{8}bit 패리티:{'N'} 정지:{1}bit")
            except serial.serialutil.SerialException as e:
                #CTkMessagebox(title="Info", message=f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
                self.add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
                logging.debug('시리얼 예외 발생: ', e)
            else:
                if not global_serial_sending:
                    msg = global_serial_device.readline()

                    if msg:
                        logging.debug(f'수신: {msg}')
                        msg = msg.decode('utf-8')
                        self.plaintext = msg.strip()
                        logging.debug(f'수신 decoded: {self.plaintext}')
                        global_serial_device.reset_input_buffer()
                    #else:
                        #logging.debug('수신: No Data in serial')
                        #CTkMessagebox(title="Info", message=f"단말에서 정보를 읽어올 수 없습니다.")
                        #app.add_status_msg(f"단말의 시리얼 포트에 도착한 복호 데이터가 없습니다.")

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        init_ui(self)
        self.c_socket = None

    def start_text_receive_thread(self):
        tcp_thread = ReceiveTCPTextThread(self.entry_host_ip.get(), self.entry_host_port.get())
        tcp_thread.start()
        self.monitor(tcp_thread)

        serial_thread = ReceiveSerialTextThread()
        serial_thread.start()
        self.monitor(serial_thread)

    def monitor(self, thread):
        #print('monitoring thread:`', thread.name)
        if thread.plaintext:
            self.entry_dectext.configure(state='normal')
            self.entry_dectext.delete(0, "end")
            self.entry_dectext.insert(0, thread.plaintext)
            self.entry_dectext.configure(state='disabled')
            self.add_status_msg(f'복호화 데이터 수신: {thread.plaintext}')
            thread.plaintext = None

        if thread.is_alive():
            # check the thread every 50ms
            self.after(50, lambda: self.monitor(thread))

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

    def limit_plaintext(self, sv):
        content = sv.get()

        if len(content) > 16: 
            #CTkMessagebox(title="알림", message="평문은 16자 이내로 입력하세요.", icon="info")
            self.add_status_msg("평문은 16자 이내로 입력하세요.")
            sv.set(content[:16])
            return False

        return True

    def read_ui_options(self):
        return do.read_ui_options(self)

    def apply_ui_options(self, options):
        do.apply_ui_options(self, options)

    def read_options_file(self):
        return do.read_options_file(self)

    def write_options_file(self, options):
        do.write_options_file(self, options)

    def dhcp_event(self):
        if self.dhcp_var.get() == 'DHCP':
            self.entry_ip.configure(state='disabled')
            self.entry_gateway.configure(state='disabled')
            self.entry_subnet.configure(state='disabled')
        else:
            self.entry_ip.configure(state='normal')
            self.entry_gateway.configure(state='normal')
            self.entry_subnet.configure(state='normal')
        self.add_status_msg(f"DHCP 설정 변경됨: DHCP={self.dhcp_var.get()}")
        print("switch toggled, current value:", self.dhcp_var.get())

    def channel_event(self):
        self.add_status_msg(f"주 통신 방식 변경됨: {self.channel_var.get()}")
        print("switch toggled, current value:", self.channel_var.get())

    def read_device_option_event(self):
        options = self.read_ui_options()
        self.read_device_options()
        options = self.read_ui_options()
        self.write_options_file(options)

    def apply_device_option_event(self):
        if self.c_socket:
            self.c_socket.close()
            self.c_socket = None

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
            #while not current_thread().stopped() or not app.stop_thread:
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

    def init_connection(self, ip, port):
        try:
            if self.c_socket:
                self.c_socket.close()
                self.c_socket = None
            self.c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.c_socket.connect((ip, port))  # connect to the server
        except socket.error:
            if self.c_socket:
                self.c_socket.close()
                self.c_socket = None
            return None
        except ValueError:
            if self.c_socket:
                self.c_socket.close()
                self.c_socket = None
            return None
        else:
            return self.c_socket

    def send_plaintext(self, plaintext):
        #msg = f'TEXT{plaintext}'
        msg = plaintext

        encoded_msg = msg.encode()
        self.c_socket.send(encoded_msg)
        self.add_status_msg(f'암호화 송신: {encoded_msg}')

    def send_ciphertext(self, ciphertext):
        print(ciphertext)
        print(type(ciphertext))
        cmd = bytes('CIPH', 'utf-8')
        print(cmd)
        msg = cmd + ciphertext
        print(msg)

        self.c_socket.send(msg)

    def get_device_ip(self):
        options = self.read_ui_options()
        return options['ip']

    def enc_button_event(self):
        plaintext = self.entry_plaintext.get()
        if not plaintext:
            self.add_status_msg("암호화할 평문(16글자 이내)를 입력하세요")
            return

        if not self.c_socket:
            if not self.init_connection(self.get_device_ip(), TEXT_PORT):
                self.add_status_msg("네트워크 연결에 실패했습니다")
                return

        self.send_plaintext(plaintext)

    def enc_serial_button_event(self):
        global global_serial_device
        global global_serial_sending

        plaintext = self.entry_plaintext.get()
        if not plaintext:
            self.add_status_msg("암호화할 평문(16글자 이내)를 입력하세요")
            return

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
            msg = bytes(f"TXT_WRT{plaintext}TXT_END\n", encoding='utf-8')
            written=global_serial_device.write(msg)
            logging.debug(f'송신: {msg}')
            logging.debug(f'송신: {written} bytes')
            self.add_status_msg(f'디바이스에 Plain Text 송신: {written}bytes => {msg}')
            time.sleep(0.3)
        finally:
            if global_serial_device:
                global_serial_device.close()
                global_serial_device = None
            global_serial_sending = False

    def dec_button_event(self):
        #ciphertext = self.ciphertextbox.get("1.0", "end-1c")
        ciphertext = self.ciphertext
        if not ciphertext:
            self.add_status_msg("암호문이 존재하지 않습니다.")
            return

        if not self.c_socket:
            if not self.init_connection(self.get_device_ip(), ENC_PORT):
                self.add_status_msg("네트워크 연결에 실패했습니다")
                return

        self.send_ciphertext(ciphertext)

    def clear_button_event(self):
        print('server thread starting...')
        self.start_text_receive_thread()

    def clear_button_event_old(self):
        self.entry_plaintext.delete(0, "end")
        self.ciphertextbox.configure(state='normal')
        self.ciphertextbox.delete("1.0", "end-1c")
        self.ciphertextbox.configure(state='disabled')
        self.entry_dectext.configure(state='normal')
        self.entry_dectext.delete(0, "end")
        self.entry_dectext.configure(state='disabled')
        self.errortextbox.configure(state='normal')
        self.errortextbox.delete("1.0", "end-1c")
        self.errortextbox.configure(state='disabled')

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

    app.stop_thread = True

if __name__ == "__main__":
    main()
