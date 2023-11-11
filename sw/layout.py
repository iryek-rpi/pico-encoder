import time

import customtkinter as ctk

TITLE = "(주)위너스 암호화 단말 PC 클라이언트"
PORT_ENC = 8501
PORT_DEC = 9501
WINDOW_WIDTH = 900#1100
WINDOW_HEIGHT = 700
SIDE_BAR_WIDTH = 400
SEND_FRAME_WIDTH = WINDOW_WIDTH - SIDE_BAR_WIDTH

def init_ui(self):
        self.repeat_operation = True # for kc test
        self.start_time = time.time()
        self.start_clear = time.time()
        self.elapsed_clear = 0

        self.comm_port = ''
        self.cipher = "AES"
        self.ciphertext = None

        self.data_to_send = None

        self.title(TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=SIDE_BAR_WIDTH,  corner_radius=0)  #,
        self.sidebar_frame.grid(row=0, column=0, sticky="ns")
        self.sidebar_frame.grid_columnconfigure(0, weight=0)

        self.send_frame = ctk.CTkFrame( self,  width=SEND_FRAME_WIDTH, corner_radius=0, fg_color='transparent')
        self.send_frame.grid(row=0, column=1, sticky="ns")
        self.send_frame.grid_columnconfigure(1, weight=1)
        self.send_frame.grid_rowconfigure(8, weight=1)

        #self.sidebar_frame.grid_rowconfigure(2, weight=1)

        SECTION_Y = 10 
        PAD_X_LABEL = 10
        PAD_X_ENTRY = 140
        PAD_X_ENTRY2 = 20
        PAD_Y_ITEM = 1
        WIDGET_DX = 30
        CENTER_WIDGET_DX = 300
        WIDGET_TOP = 10

        self.option_button = ctk.CTkButton(self.sidebar_frame, width=200, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.read_device_option_event)
        self.option_button.configure(text="단말에서 설정 읽어오기")
        self.option_button.grid(row=0, column=0, padx=WIDGET_DX*2, pady=(WIDGET_TOP, 1), sticky="ns")
        #self.option_button.columnconfigure(0, weight=1)

        # 시리얼 통신 설정
        self.label_serial = ctk.CTkLabel(self.sidebar_frame, text="시리얼 통신")
        self.label_serial.grid(row=1, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(SECTION_Y, 1), sticky="nwe")

        self.label_serial_port = ctk.CTkLabel(self.sidebar_frame, text="COM 포트")
        self.label_serial_port.grid(row=2, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=PAD_Y_ITEM, sticky="nw")
        self.entry_serial_port = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_port.grid(row=2, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=PAD_Y_ITEM, sticky="nw")

        self.label_serial_speed = ctk.CTkLabel(self.sidebar_frame, text="통신속도")
        self.label_serial_speed.grid(row=3, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=PAD_Y_ITEM, sticky="nw")
        self.entry_serial_speed = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_speed.grid(row=3, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=PAD_Y_ITEM, sticky="nw")

        self.label_serial_parity = ctk.CTkLabel(self.sidebar_frame, text="패리티 비트")
        self.label_serial_parity.grid(row=4, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=PAD_Y_ITEM, sticky="nw")
        self.entry_serial_parity = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_parity.grid(row=4, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=PAD_Y_ITEM, sticky="nw")

        self.label_serial_data = ctk.CTkLabel(self.sidebar_frame, text="데이터 비트")
        self.label_serial_data.grid(row=5, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=PAD_Y_ITEM, sticky="nw")
        self.entry_serial_data = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_data.grid(row=5, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=PAD_Y_ITEM, sticky="nw")

        self.label_serial_stop = ctk.CTkLabel(self.sidebar_frame, text="스톱 비트")
        self.label_serial_stop.grid(row=6, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=PAD_Y_ITEM, sticky="nw")
        self.entry_serial_stop = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_stop.grid(row=6, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=PAD_Y_ITEM, sticky="nw")

        # TCP 통신 설정
        self.label_network = ctk.CTkLabel(self.sidebar_frame, text="단말 네트워크 설정")
        self.label_network.grid(row=9, column=0, padx=10+WIDGET_DX, pady=(SECTION_Y,1), sticky="nwe")

        self.label_ip = ctk.CTkLabel(self.sidebar_frame, text="IP 주소")
        self.label_ip.grid(row=11, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_ip = ctk.CTkEntry(self.sidebar_frame)
        self.entry_ip.grid(row=11, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        self.label_gateway = ctk.CTkLabel(self.sidebar_frame, text="게이트웨이")
        self.label_gateway.grid(row=12, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_gateway = ctk.CTkEntry(self.sidebar_frame)
        self.entry_gateway.grid(row=12, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        self.label_subnet = ctk.CTkLabel(self.sidebar_frame, text="서브넷마스크")
        self.label_subnet.grid(row=13, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_subnet = ctk.CTkEntry(self.sidebar_frame )
        self.entry_subnet.grid(row=13, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        # TCP PEER 설정
        self.label_peer = ctk.CTkLabel(self.sidebar_frame, text="상대 단말 설정")
        self.label_peer.grid(row=20, column=0, padx=10+WIDGET_DX, pady=(SECTION_Y,1), sticky="nwe")

        self.label_peer_ip = ctk.CTkLabel(self.sidebar_frame, text="IP 주소")
        self.label_peer_ip.grid(row=21, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_peer_ip = ctk.CTkEntry(self.sidebar_frame)
        self.entry_peer_ip.grid(row=21, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        # HOST 설정
        self.label_host = ctk.CTkLabel(self.sidebar_frame, text=f"호스트 설정: {self.find_host_ip()}")
        self.label_host.grid(row=25, column=0, padx=10+WIDGET_DX, pady=(SECTION_Y,1), sticky="nwe")

        self.label_host_ip = ctk.CTkLabel(self.sidebar_frame, text="IP 주소")
        self.label_host_ip.grid(row=26, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_host_ip = ctk.CTkEntry(self.sidebar_frame)
        self.entry_host_ip.grid(row=26, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        self.label_host_port = ctk.CTkLabel(self.sidebar_frame, text="포트번호")
        self.label_host_port.grid(row=27, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_host_port = ctk.CTkEntry(self.sidebar_frame)
        self.entry_host_port.grid(row=27, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        self.sv_key = ctk.StringVar()
        self.sv_key.trace("w", lambda name, index, mode, sv=self.sv_key: self.limit_key(sv))
        self.label_key = ctk.CTkLabel(self.sidebar_frame, text="암호키(8글자 이내)")  #, placeholder_text="암호키(8
        self.label_key.grid(row=30, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(SECTION_Y,1), sticky="nw")
        self.entry_key = ctk.CTkEntry(self.sidebar_frame, textvariable=self.sv_key, fg_color="#00c177", text_color='white', placeholder_text="12345678")
        self.entry_key.grid(row=30, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=(SECTION_Y,1), sticky="nw")

        self.channel_var = ctk.StringVar(value="TCP")
        self.channel = ctk.CTkSwitch(self.sidebar_frame, text="TCP", 
                                   variable=self.channel_var, onvalue="TCP", offvalue="SERIAL")
        self.label_channel = ctk.CTkLabel(self.sidebar_frame, text="통신연결:            RS-232")  #, placeholder_text="암호키(8
        self.label_channel.grid(row=31, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(SECTION_Y,1), sticky="nw")
        self.channel.grid(row=31, column=0, padx=PAD_X_LABEL+WIDGET_DX+190, pady=(SECTION_Y,1), sticky="nw")

        self.option_button = ctk.CTkButton(self.sidebar_frame, width=200, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.apply_device_option_event)
        self.option_button.configure(text="단말에 설정 저장")
        self.option_button.grid(row=34, column=0, padx=WIDGET_DX*2, pady=(30, 30), sticky="ns")

        #=================================================================================
        # Send Frame
        self.start_server_button = ctk.CTkButton(self.send_frame, width=20, command=self.clear_status_msg)
        self.start_server_button.configure(text="삭제")
        self.start_server_button.grid(row=0, column=0, padx=(40,80), pady=(WIDGET_TOP, 5), sticky="we")

        self.label_error = ctk.CTkLabel(self.send_frame, text="상태:")
        self.label_error.grid(row=6, column=0, padx=20, pady=(30, 0), sticky="nw")
        self.errortextbox = ctk.CTkTextbox(self.send_frame, width=CENTER_WIDGET_DX, height=600, border_width = 2, border_color='gray', fg_color='light gray')
        self.errortextbox.grid(row=6, column=0, padx=90, pady=(30,0), sticky="nwe")
        self.errortextbox.configure(state='disabled')
