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

PORT_ENC = 8501
PORT_DEC = 9501
SUBNET_MASK = '255.255.255.0'
COMM_PORT = '/dev/ttyUSB0'
GATEWAY = '192.168.0.1'

WIDGET_DX = 30
CENTER_WIDGET_DX = 300

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

        self.repeat_operation = True # for kc test
        self.elapsed_time = 0
        self.start_time = time.time()
        self.start_clear = time.time()
        self.elapsed_clear = 0

        self.comm_port = ''
        self.comm_thread=None
        self.cipher = "AES"
        self.ciphertext = None
        self.c_socket = None

        self.read_options_thread = None
        self.stop_thread = False

        self.receive_plaintext_thread = None
        self.receive_ciphertext_thread = None
        self.data_to_send = None

        self.title("데이터암호화 모듈 테스트 프로그램 2023.6.30")
        self.geometry(f"{1400}x{700}")

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=220,  corner_radius=0)  #,
        self.sidebar_frame.grid(row=0, column=0, rowspan=50, sticky="nsw")

        self.send_frame = ctk.CTkFrame( self,  corner_radius=0, fg_color='transparent')
        self.send_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")

        self.receive_frame = ctk.CTkFrame(self, width=420, corner_radius=0, fg_color='transparent')
        self.receive_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")

        #self.sidebar_frame.grid_rowconfigure(2, weight=1)
        self.send_frame.grid_rowconfigure(6, weight=1)
        self.receive_frame.grid_rowconfigure(2, weight=1)


        self.option_button = ctk.CTkButton(self.sidebar_frame, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.read_option_event)
        self.option_button.configure(text="설정 읽어오기")
        self.option_button.grid(row=0, column=0, padx=10+WIDGET_DX, pady=(40, 1), sticky="nw")

        self.label_serial = ctk.CTkLabel(self.sidebar_frame, text="시리얼 통신 포트")
        self.label_serial.grid(row=1, column=0, padx=10+WIDGET_DX, pady=(20, 1), sticky="nw")

        self.entry_serial_port = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_port.grid(row=2, column=0, padx=(10+WIDGET_DX,20), pady=1, sticky="nw")

        self.label_network = ctk.CTkLabel(self.sidebar_frame, text="단말 네트워크 설정")
        self.label_network.grid(row=9, column=0, padx=10+WIDGET_DX, pady=(30,1), sticky="nw")

        self.label_ip = ctk.CTkLabel(self.sidebar_frame, text="IP")
        self.label_ip.grid(row=10, column=0, padx=15+WIDGET_DX, pady=(1,0), sticky="nw")
        self.switch_var = ctk.StringVar(value="NO-DHCP")
        self.dhcp = ctk.CTkSwitch(self.sidebar_frame, text="DHCP", command=self.dhcp_event,
                                   variable=self.switch_var, onvalue="DHCP", offvalue="NO-DHCP")
        self.dhcp.grid(row=10, column=0, padx=80+WIDGET_DX, pady=(1,0), sticky="nw")

        self.entry_ip = ctk.CTkEntry(self.sidebar_frame)
        self.entry_ip.grid(row=11, column=0, padx=10+WIDGET_DX, pady=0, sticky="nw")

        self.label_gateway = ctk.CTkLabel(self.sidebar_frame, text="gateway")
        self.label_gateway.grid(row=12, column=0, padx=15+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_gateway = ctk.CTkEntry(self.sidebar_frame)
        self.entry_gateway.grid(row=13, column=0, padx=10+WIDGET_DX, pady=0, sticky="nw")

        self.label_subnet = ctk.CTkLabel(self.sidebar_frame, text="subnet mask")
        self.label_subnet.grid(row=14, column=0, padx=15+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_subnet = ctk.CTkEntry(self.sidebar_frame )
        self.entry_subnet.grid(row=15, column=0, padx=10+WIDGET_DX, pady=0, sticky="nw")

        self.label_port = ctk.CTkLabel(self.sidebar_frame, text="port")
        self.label_port.grid(row=16, column=0, padx=15+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_port = ctk.CTkEntry(self.sidebar_frame, placeholder_text=f"{PORT_DEC}")
        self.entry_port.grid(row=17, column=0, padx=10+WIDGET_DX, pady=0, sticky="nw")

        #self.label_dec_status = ctk.CTkLabel(self.sidebar_frame, fg_color='grey', text="복호화 서버 중지됨")
        #self.label_dec_status.grid(row=17, column=0, padx=10, pady=(10,1), sticky="nw")

        self.sv_key = ctk.StringVar()
        self.sv_key.trace("w", lambda name, index, mode, sv=self.sv_key: self.limit_key(sv))
        self.label_key = ctk.CTkLabel(self.sidebar_frame, text="암호화 키(16글자 이내)")
        self.label_key.grid(row=30, column=0, padx=10+WIDGET_DX, pady=(30,1), sticky="nw")
        self.entry_key = ctk.CTkEntry(self.sidebar_frame, textvariable=self.sv_key,
                                      fg_color="#00c177", text_color='white', placeholder_text="12345678")
        self.entry_key.grid(row=31, column=0, padx=10+WIDGET_DX, pady=1, sticky="nw")

        self.label_cipher = ctk.CTkLabel(self.sidebar_frame, text="암호화 방식:")  #,
        self.label_cipher.grid(row=32, column=0, padx=10+WIDGET_DX, pady=1, sticky="nw")

        self.cipher_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["AES"],
            command=self.change_cipher_event)
        self.cipher_optionemenu.grid(row=33, column=0, padx=10+WIDGET_DX, pady=(0, 10), sticky="nw")

        self.option_button = ctk.CTkButton(self.sidebar_frame, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.apply_option_event)
        self.option_button.configure(text="설정 저장")
        self.option_button.grid(row=34, column=0, padx=10+WIDGET_DX, pady=(30, 1), sticky="nw")

        #=================================================================================
        # Send Frame
        self.clear_button = ctk.CTkButton(self.send_frame, width=20, command=self.clear_button_event)
        self.clear_button.configure(text="내용 지우기")
        self.clear_button.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="we")

        self.sv_plaintext = ctk.StringVar()
        self.sv_plaintext.trace("w", lambda name, index, mode, sv=self.sv_plaintext: self.limit_plaintext(sv))
        self.label_plaintext = ctk.CTkLabel(self.send_frame, text="평문(16글자 이내):")
        self.label_plaintext.grid(row=1, column=0, padx=20, pady=(40, 0), sticky="nw")
        self.entry_plaintext = ctk.CTkEntry(self.send_frame, textvariable=self.sv_plaintext, 
                                            width=CENTER_WIDGET_DX, placeholder_text="16자 이내의 암호화할 데이터를 입력하세요")
        self.entry_plaintext.grid(row=1, column=0, padx=150, pady=(40,0), sticky="nwe")

        self.enc_button = ctk.CTkButton(self.send_frame, width=200, command=self.enc_button_event)
        self.enc_button.configure(text="암호화 요청", bg_color='#aa3333', fg_color='#bb3333')
        self.enc_button.grid(row=2, column=0, padx=20, pady=(30, 0))#, sticky="we")

        self.label_ciphertext = ctk.CTkLabel(self.send_frame, text="암호문:")
        self.label_ciphertext.grid(row=3, column=0, padx=20, pady=(30, 0), sticky="nw")
        self.ciphertextbox = ctk.CTkTextbox(self.send_frame, width=CENTER_WIDGET_DX, height=80, border_width = 2, border_color='gray', fg_color='light gray')
        self.ciphertextbox.grid(row=3, column=0, padx=70, pady=(30,0), sticky="nwe")
        self.ciphertextbox.configure(state='disabled')

        self.dnc_button = ctk.CTkButton(self.send_frame, width=200, command=self.dec_button_event)
        self.dnc_button.configure(text="복호화 요청", fg_color='#555599')
        self.dnc_button.grid(row=4, column=0, padx=20, pady=(30, 0))#, sticky="we")

        self.label_dectext = ctk.CTkLabel(self.send_frame, text="복호문:")
        self.label_dectext.grid(row=5, column=0, padx=20, pady=(30, 0), sticky="nw")
        self.entry_dectext = ctk.CTkEntry(self.send_frame, width=CENTER_WIDGET_DX, border_width = 2, border_color='gray', fg_color='light gray')
        self.entry_dectext.grid(row=5, column=0, padx=70, pady=(30,0), sticky="nwe")
        self.entry_dectext.configure(state='disabled')

        self.label_error = ctk.CTkLabel(self.send_frame, text="상태:")
        self.label_error.grid(row=6, column=0, padx=20, pady=(30, 0), sticky="nw")
        self.errortextbox = ctk.CTkTextbox(self.send_frame, width=CENTER_WIDGET_DX, height=220, border_width = 2, border_color='gray', fg_color='light gray')
        self.errortextbox.grid(row=6, column=0, padx=70, pady=(30,0), sticky="nwe")
        self.errortextbox.configure(state='disabled')
        #=================================================================================
        # create textbox
        self.history_button = ctk.CTkButton(self.receive_frame, command=self.history_clear_event)
        self.history_button.configure(text="처리 기록 삭제")#, bg_color='#889933', fg_color='#889933')
        self.history_button.grid(row=0, column=0, padx=30, pady=(15, 5), sticky="nswe")

        self.history_textbox = ctk.CTkTextbox(self.receive_frame, width=420, border_width = 2, border_color='gray', fg_color='light gray')
        self.history_textbox.grid(row=2, column=0, padx=(20, 20), pady=(40, 60), sticky="nsew")
        #self.history_textbox.insert('0.0', "처리 기록\n")
        self.history_textbox.configure(state='disabled')
        #self.receive_textbox.configure(bg_color='blue', fg_color='blue', border_color='blue')

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
        options = {}
        options['comm'] = self.entry_serial_port.get()
        if self.switch_var.get() == "DHCP":
            options['dhcp'] = 1
        else:
            options['dhcp'] = 0
        options['ip'] = self.entry_ip.get()
        options['subnet'] = self.entry_subnet.get()
        options['gateway'] = self.entry_gateway.get()
        options['port'] = self.entry_port.get()
        options['key'] = self.entry_key.get()

        return options

    def apply_ui_options(self, options):
        app.entry_serial_port.delete(0, "end")
        app.entry_serial_port.insert(0, options["comm"])

        if options['dhcp'] and self.switch_var.get() == "NO-DHCP":
            self.switch_var.set("DHCP")
            self.dhcp_event()
            self.entry_ip.configure(state='normal')
            self.entry_gateway.configure(state='normal')
            self.entry_subnet.configure(state='normal')

            self.entry_ip.delete(0, "end")
            self.entry_ip.insert(0, options["ip"])
            self.entry_gateway.delete(0, "end")
            self.entry_gateway.insert(0, options["gateway"])
            self.entry_subnet.delete(0, "end")
            self.entry_subnet.insert(0, options["subnet"])

            #self.entry_ip.configure(state='disabled')
            #self.entry_gateway.configure(state='disabled')
            #self.entry_subnet.configure(state='disabled')
        elif not options['dhcp'] and self.switch_var.get() == "DHCP":
            self.switch_var.set("NO-DHCP")
            self.dhcp_event()

            self.entry_ip.delete(0, "end")
            self.entry_ip.insert(0, options["ip"])
            self.entry_gateway.delete(0, "end")
            self.entry_gateway.insert(0, options["gateway"])
            self.entry_subnet.delete(0, "end")
            self.entry_subnet.insert(0, options["subnet"])
        else:
            self.entry_ip.configure(state='normal')
            self.entry_gateway.configure(state='normal')
            self.entry_subnet.configure(state='normal')

            self.entry_ip.delete(0, "end")
            self.entry_ip.insert(0, options["ip"])
            self.entry_gateway.delete(0, "end")
            self.entry_gateway.insert(0, options["gateway"])
            self.entry_subnet.delete(0, "end")
            self.entry_subnet.insert(0, options["subnet"])

            #self.entry_ip.configure(state='disabled')
            #self.entry_gateway.configure(state='disabled')
            #self.entry_subnet.configure(state='disabled')

        self.entry_port.delete(0, "end")
        self.entry_port.insert(0, options["port"])
        self.entry_key.delete(0, "end")
        self.entry_key.insert(0, options["key"])

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
