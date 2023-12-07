import os
import sys
import time
from threading import Thread
import logging
import serial
import socket
import flet as ft

from w5500 import constants as c
import controls

# config a logger using default logger
logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

tcp_thread = None
serial_thread = None

global_page = None
global_serial_device=None
global_serial_sending=None
SERIAL1_TIMEOUT = 50

def find_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1)) # doesn't even have to be reachable
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class ReceiveTCPTextThread(Thread):
    #global app
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
                    #fcntl.fcntl(conn, fcntl.F_SETFL, os.O_NONBLOCK)
                    #conn.setblocking(False)
                    data = conn.recv(1024)
                    if not data:
                        print('No data received from tcp socket')
                        break
                    self.plaintext = data.decode('utf-8')
                    controls.add_history(f'TCP/IP: {self.plaintext}')
                    print('PlainText received through socket: ', data)
                conn.close()
            
        except Exception as e:
            print('Exception: ', e)

def get_serial_settings(settings):
    return settings['serial_port'], settings['serial_speed'], settings['parity'], settings['data_size'], settings['stopbit']

def init_serial(serial_settings):
    global global_serial_device
    global global_serial_sending

    port, baud, parity, data, stopbits = serial_settings 
    try:
        return serial.Serial(port=port, baudrate=int(baud), bytesize=int(data), 
                             parity=parity, stopbits=int(stopbits), write_timeout=0.02) 
    except serial.serialutil.SerialException as e:
        #add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        logging.info('시리얼 예외 발생: ', e)
        controls.add_history(f"시리얼 연결 오류: COM 포트({port})를 확인하세요.")
        #if controls.g_page:
        #    controls.alert_dlg.content = f"시리얼 연결 오류: COM 포트({port})를 확인하세요."
        #    controls.g_page.dialog = controls.alert_dlg
        #    controls.alert_dlg.open = True
        #    controls.g_page.update()
        return None

class ReceiveSerialTextThread(Thread):
    def __init__(self, serial_settings):
        global global_serial_device
        global global_serial_sending

        super().__init__()

        self.plaintext = None
        self.name = 'Serial Text Thread'

        global_serial_device = init_serial(serial_settings)

    def run(self):
        global app
        global global_serial_device
        global global_serial_sending

        while True:
            try:
                if not global_serial_sending:
                    logging.info(f'Waiting for serial data from {global_serial_device}...')
                    msg = global_serial_device.readline()
                    logging.info(f'수신: {msg} from {global_serial_device}')
                    if msg:
                        logging.info(f'수신: {msg}')
                        msg = msg.decode('utf-8')
                        self.plaintext = msg.strip()
                        controls.add_history(f'SERIAL: {self.plaintext}')
                        logging.info(f'수신 decoded: {self.plaintext}')
                        global_serial_device.reset_input_buffer()
                    #else:
                        #logging.debug('수신: No Data in serial')
                        #CTkMessagebox(title="Info", message=f"단말에서 정보를 읽어올 수 없습니다.")
                        #app.add_status_msg(f"단말의 시리얼 포트에 도착한 복호 데이터가 없습니다.")
            except serial.serialutil.SerialException as e:
                #CTkMessagebox(title="Info", message=f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
                #self.add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
                logging.info('시리얼 예외 발생: ', e)

def start_server(settings):
    global tcp_thread
    global serial_thread

    print(f'settings[chan]: {settings["chan"]}')
    #if settings['chan'] == 'tcp':
    if not tcp_thread:
        tcp_thread = ReceiveTCPTextThread(settings['host_ip'], settings['host_port'])
        tcp_thread.start()
    #else:
    if not serial_thread:
        serial_thread = ReceiveSerialTextThread(get_serial_settings(settings))
        if global_serial_device:
            serial_thread.start()
        else:
            serial_thread = None

def serial_send_plaintext(settings, text):
    global global_serial_device
    global global_serial_sending

    logging.info(f'sending plaintext: {text}')
    try:
        if not global_serial_device:
            global_serial_device = init_serial(get_serial_settings(settings))
        msg = bytes(f"TXT_WRT{text}TXT_END\n", encoding='utf-8')
        logging.info(f'msg: {msg}')
        global_serial_sending = True
        time.sleep(0.05)
        written=global_serial_device.write(msg)
        global_serial_sending = False
        logging.info(f'{written} bytes 송신: {msg} ')
        #self.add_status_msg(f'디바이스에 Plain Text 송신: {written}bytes => {msg}')
    except serial.serialutil.SerialException as e:
        #self.add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        logging.info('시리얼 예외 발생: ', e)

def tcp_send_plaintext(settings, text):
    try:
        logging.info(f'sending plaintext: {text}')
        #msg = bytes(f"TXT_WRT{text}TXT_END\n", encoding='utf-8')
        msg = bytes(text, encoding='utf-8')
        logging.info(f'msg: {msg}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"ip: {settings['device_ip']} c.TEXT_PORT: {c.TEXT_PORT}")
        sock.connect((settings['device_ip'], c.TEXT_PORT))
        written = sock.sendall(msg)
        print(f'{written} bytes 송신: {msg} to {settings["device_ip"]}:{c.TEXT_PORT}')
        #logging.info(f'{written} bytes 송신: {msg} ')
    except serial.serialutil.SerialException as e:
        #self.add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        logging.info('시리얼 예외 발생: ', e)
