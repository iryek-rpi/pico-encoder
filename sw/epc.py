import sys
import time
import datetime
import threading
from threading import Thread
from threading import current_thread
import logging

import json
import serial
import tkinter
import tkinter.filedialog as fdlg
import tkinter.messagebox
import customtkinter as ctk
#from CTkMessagebox import CTkMessagebox
import socket

from layout import *
import device_options as do
from crypto_ex import *

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

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        init_ui(self)

    def add_status_msg(self, msg):
        self.errortextbox.configure(state='normal')
        self.errortextbox.insert('0.0', "\n" + msg + "\n")
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
        app.entry_serial_port.delete(0, "end")
        app.entry_serial_port.insert(0, options["comm"])

        do.apply_ui_options(self, options)

    def read_options_file(self):
        options = {}

        with open("k2_config.txt", "r") as f:
            lines = f.readlines()
            options['comm'] = lines[0].split("comm:")[1].strip()
            dhcp =  lines[1].split("dhcp:")[1].strip()
            if dhcp == 'true':
                options['dhcp'] = 1
            else:
                options['dhcp'] = 0
            options['ip'] = lines[2].split("ip:")[1].strip()
            options['gateway'] = lines[3].split("gateway:")[1].strip()
            options['subnet'] = lines[4].split("subnet:")[1].strip()
            options['port'] = lines[5].split("port:")[1].strip()
            options['key'] = lines[6].split("key:")[1].strip()

        return options

    def write_options_file(self, options):
        with open('k2_config.txt', 'w') as f:
            f.write("comm:" + options["comm"] + "\n")
            if options["dhcp"]:
                f.write("dhcp:" + 'true' + "\n")
            else:
                f.write("dhcp:" + 'false' + "\n")
            f.write("ip:" + options["ip"] + "\n")
            f.write("gateway:" + options["gateway"] + "\n")
            f.write("subnet:" + options["subnet"] + "\n")
            f.write("port:" + options["port"] + "\n")
            f.write("key:" + options["key"] + "\n")

    def dhcp_event(self):
        #if self.switch_var.get() == 'DHCP':
            #self.entry_ip.configure(state='disabled')
            #self.entry_gateway.configure(state='disabled')
            #self.entry_subnet.configure(state='disabled')
        #else:
        self.entry_ip.configure(state='normal')
        self.entry_gateway.configure(state='normal')
        self.entry_subnet.configure(state='normal')
        self.add_status_msg(f"DHCP 설정 변경됨: DHCP={self.switch_var.get()}")
        print("switch toggled, current value:", self.switch_var.get())

    def read_option_event(self):
        options = self.read_ui_options()
        self.read_device_options()
        options = self.read_ui_options()
        self.write_options_file(options)

    def apply_option_event(self):
        if self.c_socket:
            self.c_socket.close()
            self.c_socket = None

        self.write_device_options()

        options = self.read_ui_options()
        self.write_options_file(options)

    def read_device_options(self):
        try:
            device = None
            self.comm_port = self.entry_serial_port.get()
            device = serial.Serial(port=self.comm_port, baudrate=BAUD_RATE, bytesize=8, parity='N', stopbits=1, timeout=SERIAL1_TIMEOUT, write_timeout=SERIAL1_TIMEOUT) 
            self.add_status_msg(f"시리얼 연결됨: COM 포트({self.comm_port}) 속도:{BAUD_RATE}bps 데이터:{8}bit 패리티:{'N'} 정지:{1}bit")
        except serial.serialutil.SerialException as e:
            #CTkMessagebox(title="Info", message=f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
            self.add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
            logging.debug('시리얼 예외 발생: ', e)
        else:
            #while not current_thread().stopped() or not app.stop_thread:
            device.write('CNF_REQ\n'.encode())
            msg = device.readline()

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
                    device.reset_input_buffer()
                else:
                    self.add_status_msg(f'Partial msg received: {msg}')
            else:
                logging.debug('수신: No Data')
                #CTkMessagebox(title="Info", message=f"단말에서 정보를 읽어올 수 없습니다.")
                self.add_status_msg(f"단말에서 정보를 읽어올 수 없습니다. msg:{msg}")

        finally:
            if device:
                device.close()
                device = None

    def write_device_options(self):

        try:
            self.comm_port = self.entry_serial_port.get()
            device = serial.Serial(port=self.comm_port, baudrate=BAUD_RATE, bytesize=8, parity='N', stopbits=1, timeout=SERIAL1_TIMEOUT, write_timeout=SERIAL1_TIMEOUT) 
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
            written=device.write(msg)
            logging.debug(f'송신: {msg}')
            logging.debug(f'송신: {written} bytes')
            self.add_status_msg(f'디바이스에 설정 송신: {written}bytes => {msg}')
            time.sleep(0.3)
        finally:
            device.close()
            device = None

    def find_host_ip():
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"Hostname: {hostname}")
        print(f"IP Address: {ip_address}")

    def init_connection(self):
        try:
            if self.c_socket:
                self.c_socket.close()
                self.c_socket = None
            _ip = self.entry_ip.get()
            _port = self.entry_port.get()
            self.c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.c_socket.connect((_ip, int(_port)))  # connect to the server
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
        msg = f'TEXT{plaintext}'
        self.history_textbox.configure(state='normal')
        self.history_textbox.insert('0.0', '요청: ' + plaintext)
        self.history_textbox.insert('0.0', '\n')
        self.history_textbox.configure(state='disabled')

        encoded_msg = msg.encode()
        self.c_socket.send(encoded_msg)
        self.add_status_msg(f'암호화 송신: {encoded_msg}')

        iv_c = self.c_socket.recv(64)
        self.add_status_msg(f'암호화 수신: {iv_c}')

        #self.c_socket.close()
        #self.c_socket = None

        print('iv_c: ')
        print(iv_c)
        print(type(iv_c))

        self.ciphertext = iv_c
        self.ciphertextbox.configure(state='normal')
        self.ciphertextbox.delete("1.0", "end-1c")
        self.ciphertextbox.insert(tkinter.END, iv_c)
        self.ciphertextbox.configure(state='disabled')

        self.history_textbox.configure(state='normal')
        self.history_textbox.insert('0.0', '응답: ')
        self.history_textbox.insert('1.7', self.ciphertext)
        self.history_textbox.insert('0.0', '\n')
        elapsed = str(datetime.timedelta(seconds=int(self.elapsed_time)))
        self.history_textbox.insert('0.0', '암호화 경과시간: ')
        self.history_textbox.insert('1.10', elapsed)
        self.history_textbox.insert('0.0', '\n\n')
        self.history_textbox.configure(state='disabled')

        print('self.ciphertext: ')
        print(self.ciphertext)
        print(type(self.ciphertext))

    def send_ciphertext(self, ciphertext):
        self.history_textbox.configure(state='normal')
        self.history_textbox.insert('0.0', '요청: ')
        self.history_textbox.insert('1.7', ciphertext)
        self.history_textbox.insert('0.0', '\n')
        self.history_textbox.configure(state='disabled')

        print(ciphertext)
        print(type(ciphertext))
        cmd = bytes('CIPH', 'utf-8')
        print(cmd)
        msg = cmd + ciphertext
        print(msg)

        self.c_socket.send(msg)
        plaintext = self.c_socket.recv(1024)
        self.add_status_msg(f'복호화 송신: {msg}')
        self.add_status_msg(f'복호화 수신: {plaintext}')
        #self.c_socket.close()
        #self.c_socket = None

        self.entry_dectext.configure(state='normal')
        self.entry_dectext.delete(0, "end")
        self.entry_dectext.insert(tkinter.END, plaintext.decode('utf-8'))
        self.entry_dectext.configure(state='disabled')

        self.history_textbox.configure(state='normal')
        self.history_textbox.insert('0.0', '응답: ' + plaintext.decode('utf-8'))
        self.history_textbox.insert('0.0', '\n')
        elapsed = str(datetime.timedelta(seconds=int(self.elapsed_time)))
        self.history_textbox.insert('0.0', '복호화 경과시간: ')
        self.history_textbox.insert('1.10', elapsed)
        self.history_textbox.insert('0.0', '\n\n')
        self.history_textbox.configure(state='disabled')

    def enc_button_event(self):
        plaintext = self.entry_plaintext.get()
        if not plaintext:
            #CTkMessagebox(title="Info", message="암호화할 평문(16글자 이내)를 입력하세요")
            self.add_status_msg("암호화할 평문(16글자 이내)를 입력하세요")
            return

        if not self.c_socket:
            if not self.init_connection():
                #CTkMessagebox(title="Error", message=f"네트워크 연결에 실패했습니다")
                self.add_status_msg("네트워크 연결에 실패했습니다")
                return

        self.elapsed_time = time.time() - self.start_time
        self.send_plaintext(plaintext)
        self.after(2000, self.enc_button_event)

        self.elapsed_clear = time.time() - self.start_clear
        if self.elapsed_clear > 600:
            self.errortextbox.configure(state='normal')
            self.errortextbox.delete("1.0", "end-1c")
            self.errortextbox.configure(state='disabled')
            self.history_textbox.configure(state='normal')
            self.history_textbox.delete("1.0", "end-1c")
            self.history_textbox.configure(state='disabled')
            self.start_clear = time.time()

    def dec_button_event(self):
        #ciphertext = self.ciphertextbox.get("1.0", "end-1c")
        ciphertext = self.ciphertext
        if not ciphertext:
            #CTkMessagebox(title="Info", message=f"암호문이 존재하지 않습니다.")
            self.add_status_msg("암호문이 존재하지 않습니다.")
            return

        if not self.c_socket:
            if not self.init_connection():
                #CTkMessagebox(title="Error", message=f"네트워크 연결에 실패했습니다")
                self.add_status_msg("네트워크 연결에 실패했습니다")
                return

        self.elapsed_time = time.time() - self.start_time
        self.send_ciphertext(ciphertext)
        self.after(2000, self.dec_button_event)

        self.elapsed_clear = time.time - self.start_clear
        if self.elapsed_clear > 600:
            self.errortextbox.configure(state='normal')
            self.errortextbox.delete("1.0", "end-1c")
            self.errortextbox.configure(state='disabled')
            self.history_textbox.configure(state='normal')
            self.history_textbox.delete("1.0", "end-1c")
            self.history_textbox.configure(state='disabled')
            self.start_clear = time.time()

    def history_clear_event(self):
        self.history_textbox.configure(state='normal')
        self.history_textbox.delete("1.0", "end-1c")
        self.history_textbox.configure(state='disabled')

    def clear_button_event(self):
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


if __name__ == "__main__":

    app = App()

    options = app.read_options_file()
    app.apply_ui_options(options)
    app.comm_port = options["comm"]

    app.mainloop()

    app.stop_thread = True
