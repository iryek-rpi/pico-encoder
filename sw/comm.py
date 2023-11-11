import sys
import time
from threading import Thread
import logging
import serial
import socket
import select
import asyncio
import controls

# config a logger using default logger
logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

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
        #self.ip = ip
        #self.port = port
        self.ip = '192.168.2.159'
        self.port = 8503
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
                    controls.add_history(f'TCP/IP: {data}')
                    print('PlainText received through socket: ', data)
                    self.plaintext = data.decode('utf-8')
                    #app.add_status_msg(f'복호화 데이터 수신: {data}')
                conn.close()
            
        except Exception as e:
            print('Exception: ', e)

class ReceiveSerialTextThread(Thread):
    def __init__(self):
        super().__init__()

        self.plaintext = None
        self.name = 'Serial Text Thread'
        self.comm_port = "COM33"

    def run(self):
        global app
        global global_serial_device
        global global_serial_sending

        while True:
            try:
                if not global_serial_device:
                    print('Creating serial device')
                    global_serial_device = serial.Serial(port="COM33", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.02, write_timeout=0.02) 
                if not global_serial_sending:
                    msg = global_serial_device.readline()
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

def init_serial(settings):
    global global_serial_device
    global global_serial_sending

    try:
        if global_serial_device:
            global_serial_device.close()
        global_serial_device = serial.Serial(port="COM33", baudrate=9600, bytesize=8, parity=None, stopbits=1, timeout=50, write_timeout=50) 
        #self.add_status_msg(f"시리얼 연결됨: COM 포트({self.comm_port}) 속도:{BAUD_RATE}bps 데이터:{8}bit 패리티:{'N'} 정지:{1}bit")
        return global_serial_device
    except serial.serialutil.SerialException as e:
        #add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        logging.info('시리얼 예외 발생: ', e)
    processed_msg = handler(b64, fixed_binary_key)
    if not processed_msg:
        print('TCP processed result Empty')
        processed_msg = bytes('***BAD DATA***', 'utf-8')
    if channel == utils.CH_TCP:
        print('sending processed msg: ', processed_msg, ' to ', dest_ip, ':', dest_port)
        pn.send_data(processed_msg, dest_ip, dest_port)
        #await pn.send_data(processed_msg, dest_ip, dest_port)
    else:
        print('sending processed msg: ', processed_msg, ' to ', uart)
        uart.write(processed_msg)

def serial_send_plaintext(settings, text):
    global global_serial_device
    global global_serial_sending

    logging.info(f'sending plaintext: {text}')
    while global_serial_sending:
        time.sleep(0.05)
    try:
        if not global_serial_device:
            global_serial_device = init_serial(settings)
        msg = bytes(f"TXT_WRT{text}TXT_END\n", encoding='utf-8')
        logging.info(f'msg: {msg}')
        global_serial_sending = True
        written=global_serial_device.write(msg)
        global_serial_sending = False
        logging.info(f'{written} bytes 송신: {msg} ')
        #self.add_status_msg(f'디바이스에 Plain Text 송신: {written}bytes => {msg}')
    except serial.serialutil.SerialException as e:
        #self.add_status_msg(f"시리얼 연결 오류: COM 포트({self.comm_port})를 확인하세요.")
        logging.info('시리얼 예외 발생: ', e)
