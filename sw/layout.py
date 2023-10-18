import time

import customtkinter as ctk

TITLE = "(주)위너스 암호화 단말 PC 클라이언트"
PORT_ENC = 8501
PORT_DEC = 9501

def init_ui(self):
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

        self.title(TITLE)
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

        SECTION_Y = 20 
        PAD_X_LABEL = 10
        PAD_X_ENTRY = 140
        PAD_X_ENTRY2 = 20
        PAD_Y_ITEM = 1
        WIDGET_DX = 30
        CENTER_WIDGET_DX = 300


        self.option_button = ctk.CTkButton(self.sidebar_frame, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.read_option_event)
        self.option_button.configure(text="설정 읽어오기")
        self.option_button.grid(row=0, column=0, padx=WIDGET_DX*2, pady=(40, 1), sticky="nwe")

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

        self.label_serial_databit = ctk.CTkLabel(self.sidebar_frame, text="데이터 비트")
        self.label_serial_databit.grid(row=5, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=PAD_Y_ITEM, sticky="nw")
        self.entry_serial_databit = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_databit.grid(row=5, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=PAD_Y_ITEM, sticky="nw")

        self.label_serial_stopbit = ctk.CTkLabel(self.sidebar_frame, text="스톱 비트")
        self.label_serial_stopbit.grid(row=6, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=PAD_Y_ITEM, sticky="nw")
        self.entry_serial_stopbit = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_stopbit.grid(row=6, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=PAD_Y_ITEM, sticky="nw")

        # TCP 통신 설정
        self.label_network = ctk.CTkLabel(self.sidebar_frame, text="단말 네트워크 설정")
        self.label_network.grid(row=9, column=0, padx=10+WIDGET_DX, pady=(SECTION_Y,1), sticky="nwe")

        self.switch_var = ctk.StringVar(value="NO-DHCP")
        self.dhcp = ctk.CTkSwitch(self.sidebar_frame, text="DHCP", command=self.dhcp_event,
                                   variable=self.switch_var, onvalue="DHCP", offvalue="NO-DHCP")
        self.dhcp.grid(row=10, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")

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

        self.label_port = ctk.CTkLabel(self.sidebar_frame, text="포트번호")
        self.label_port.grid(row=14, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_port = ctk.CTkEntry(self.sidebar_frame, placeholder_text=f"{PORT_DEC}")
        self.entry_port.grid(row=14, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        # TCP PEER 설정
        self.label_peer = ctk.CTkLabel(self.sidebar_frame, text="상대 단말 설정")
        self.label_peer.grid(row=20, column=0, padx=10+WIDGET_DX, pady=(SECTION_Y,1), sticky="nwe")

        self.label_peer_ip = ctk.CTkLabel(self.sidebar_frame, text="IP 주소")
        self.label_peer_ip.grid(row=21, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_peer_ip = ctk.CTkEntry(self.sidebar_frame)
        self.entry_peer_ip.grid(row=21, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        self.label_peer_port = ctk.CTkLabel(self.sidebar_frame, text="포트번호")
        self.label_peer_port.grid(row=22, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_peer_port = ctk.CTkEntry(self.sidebar_frame)
        self.entry_peer_port.grid(row=22, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        # HOST 설정
        self.label_host = ctk.CTkLabel(self.sidebar_frame, text="호스트 설정")
        self.label_host.grid(row=25, column=0, padx=10+WIDGET_DX, pady=(SECTION_Y,1), sticky="nwe")

        self.label_host_ip = ctk.CTkLabel(self.sidebar_frame, text="IP 주소")
        self.label_host_ip.grid(row=26, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_host_ip = ctk.CTkEntry(self.sidebar_frame)
        self.entry_host_ip.grid(row=26, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        self.label_host_port = ctk.CTkLabel(self.sidebar_frame, text="포트번호")
        self.label_host_port.grid(row=27, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        self.entry_host_port = ctk.CTkEntry(self.sidebar_frame)
        self.entry_host_port.grid(row=27, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        #self.label_dec_status = ctk.CTkLabel(self.sidebar_frame, fg_color='grey', text="복호화 서버 중지됨")
        #self.label_dec_status.grid(row=17, column=0, padx=10, pady=(10,1), sticky="nw")

        self.sv_key = ctk.StringVar()
        self.sv_key.trace("w", lambda name, index, mode, sv=self.sv_key: self.limit_key(sv))
        self.label_key = ctk.CTkLabel(self.sidebar_frame, text="암호키(8글자 이내)")  #, placeholder_text="암호키(8
        self.label_key.grid(row=30, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(SECTION_Y,1), sticky="nw")
        self.entry_key = ctk.CTkEntry(self.sidebar_frame, textvariable=self.sv_key, fg_color="#00c177", text_color='white', placeholder_text="12345678")
        self.entry_key.grid(row=30, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=(SECTION_Y,1), sticky="nw")

        #self.label_cipher = ctk.CTkLabel(self.sidebar_frame, text="암호화 방식:")  #,
        #self.label_cipher.grid(row=32, column=0, padx=PAD_X_LABEL+WIDGET_DX, pady=(1,0), sticky="nw")
        #self.cipher_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["AES"], command=self.change_cipher_event)
        #self.cipher_optionemenu.grid(row=32, column=0, padx=(PAD_X_ENTRY+WIDGET_DX,PAD_X_ENTRY2), pady=0, sticky="nw")

        self.option_button = ctk.CTkButton(self.sidebar_frame, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.apply_option_event)
        self.option_button.configure(text="설정 저장")
        self.option_button.grid(row=34, column=0, padx=WIDGET_DX*2, pady=(30, 1), sticky="nwe")

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