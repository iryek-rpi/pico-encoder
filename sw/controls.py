from datetime import datetime

import flet as ft
import comm
import w5500.constants as c
from pprint import pp

ENC_COLUMN_WIDTH = 1000
LEFT_TITLE_WIDTH = 140
MID_TITLE_WIDTH = 60 

TITLE_ALIGN = ft.TextAlign.CENTER
MID_TITLE_ALIGN = ft.TextAlign.END

TITLE_WEIGHT = ft.FontWeight.BOLD
TITLE_SIZE = 18

LONG_FIELD = 180
SHORT_FIELD = 100
MID_FIELD = 120
INPUT_HINT = "전송할 데이터를 입력하세요"

GROUP_WIDTH_MARGIN = 50
GROUP_WIDTH = LEFT_TITLE_WIDTH + LONG_FIELD + GROUP_WIDTH_MARGIN
GROUP_TITLE_HEIGHT = 50

BUTTON_HEIGHT = 40
BUTTON_BAR_HEIGHT = 60
GROUP_HEIGHT = 500
WINC_WINDOW_WIDTH = GROUP_WIDTH * 3 + 27 + 50
WINC_WINDOW_HEIGHT = 620

g_page = None
info_text = ft.Text('Dropdown focus count', width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT)

def on_portlist_focus(e):
    ports = comm.serial_ports()
    e.control.options.clear()
    if ports:
        for port in ports:
            e.control.options.append(ft.dropdown.Option(port))
    e.control.page.update()

def read_from_device(e):
    pass

button_row = ft.Container( bgcolor=ft.colors.RED, 
                content=ft.Row(spacing = 50, width = WINC_WINDOW_WIDTH, height = BUTTON_BAR_HEIGHT, alignment=ft.MainAxisAlignment.CENTER,
                            controls = [
                                ft.FilledButton("단말에서 설정 읽어오기", on_click=read_from_device, width=200, height=BUTTON_HEIGHT,
                                        style=ft.ButtonStyle(shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),})),
                                ft.FilledButton("단말에 설정 저장", on_click=read_from_device, width=200, height=BUTTON_HEIGHT, 
                                        style=ft.ButtonStyle(shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),})),
                            ]))
    
    

class OptionRow(ft.Row):
    def __init__(self, label, control, options):
        self.option_label = ft.Text(label, width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT)
        if control == ft.TextField:
            self.option_control = ft.TextField(width=LONG_FIELD)
        elif control == ft.Dropdown:
            self.option_control = ft.Dropdown(width=LONG_FIELD,
                                value=options[1][options[0]],
                                options=[ft.dropdown.Option(option) for option in options[1]],
                            )
        elif control == ft.RadioGroup:
            self.option_control = ft.RadioGroup(value=options[1][options[0]], content = ft.Row([ft.Radio(value=option, label=option) for option in options[1]]))
        else:
            assert False, f"Unknown control type: {control}"
        super().__init__(spacing=5, width=ENC_COLUMN_WIDTH, alignment=ft.MainAxisAlignment.START,
                    controls=[self.option_label, self.option_control])
    
    def get_value(self):
        return self.controls[1].value

    def set_value(self, value):
        self.controls[1].value = value

class OptionGroup(ft.Container):
    def __init__(self, title, options):
        self.group_title = ft.Container(ft.Text(title, weight=TITLE_WEIGHT, size=TITLE_SIZE), alignment=ft.alignment.center, 
                                        bgcolor=ft.colors.BLUE_GREY_100, width=GROUP_WIDTH, height=GROUP_TITLE_HEIGHT)
        self.options = options
        content = ft.Column(scroll=ft.ScrollMode.HIDDEN, expand=True, alignment=ft.MainAxisAlignment.START, 
                         controls=[self.group_title]+self.options, width=GROUP_WIDTH)
        super().__init__(content=content, width=GROUP_WIDTH, height=GROUP_HEIGHT, bgcolor=ft.colors.YELLOW_ACCENT_100)


cfg_channel = OptionRow("통신채널:", ft.RadioGroup, c.CHANNEL_OPTIONS)
cfg_host_ip = OptionRow("호스트 IP:", ft.TextField, [])
cfg_host_port = OptionRow("호스트 포트:", ft.TextField, [])

cfg_serial_port = OptionRow("시리얼 포트:", ft.TextField, [])
cfg_serial_port_list = OptionRow("시리얼 포트 목록:", ft.Dropdown, (0, comm.serial_ports()))
cfg_serial_port_list.option_control.on_focus = on_portlist_focus
cfg_serial_speed = OptionRow("시리얼 속도:", ft.Dropdown, c.SPEED_OPTIONS)
cfg_serial_parity = OptionRow("패리티 비트:", ft.Dropdown, c.PARITY_OPTIONS)
cfg_serial_data = OptionRow("데이터 비트:", ft.Dropdown, c.DATA_OPTIONS)
cfg_serial_stop = OptionRow("스톱 속도:", ft.Dropdown, c.STOP_OPTIONS)

cfg_device_ip = OptionRow("단말 IP:", ft.TextField, [])
cfg_gateway = OptionRow("게이트웨이:", ft.TextField, [])
cfg_subnet = OptionRow("서브넷마스크:", ft.TextField, [])
cfg_peer_ip = OptionRow("상대 단말 IP:", ft.TextField, [])
cfg_key = OptionRow("암호키:", ft.TextField, [])
ports = comm.serial_ports()
#custom_serial_speed = OptionRow("시리얼 속도:", ft.Dropdown, (0, ports))
#custom_serial_speed.option_control.options.clear()
#custom_serial_speed.option_control.options.append(ft.dropdown.Option(f"없음"))
#custom_serial_speed.option_control.value=0
#custom_serial_speed.option_control.on_focus = on_dropdown_focus
og_host = OptionGroup("호스트 설정", 
            [cfg_channel, cfg_host_ip, cfg_host_port])
og_serial = OptionGroup("시리얼 통신 설정", 
            [cfg_serial_port, cfg_serial_port_list, cfg_serial_speed, cfg_serial_parity, cfg_serial_data, cfg_serial_stop])
og_device = OptionGroup("단말 설정", 
            [cfg_device_ip, cfg_gateway, cfg_subnet, cfg_peer_ip, cfg_key])

def add_history(msg):
    global history
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    history.value = f'{now}: {msg}\n{history.value}'
    history.update()
    
def request_encryption(e):
    global plain_text
    text = plain_text.value if plain_text.value != '' else plain_text.hint_text
    if text == '' or text.startswith(INPUT_HINT):
        alert_dlg.content = ft.Text(INPUT_HINT)
        e.control.page.dialog = alert_dlg
        alert_dlg.open = True
    else:
        plain_text.value = ''
        plain_text.hint_text = text 
        settings = get_settings()
        if settings['chan'] == 'serial':
            comm.serial_send_plaintext(settings, text)
        else:
            comm.tcp_send_plaintext(settings, text)
    e.control.page.update()

def start_server(e):
    comm.start_server(get_settings())

def clear_history(e):
    history.value = ''
    e.control.page.update()
    print("기록 삭제됨")

def close_dlg(e):
    alert_dlg.open = False
    e.control.page.update()

def validate_required_text_field(e):
        if e.control.value == "":
            e.control.error_text = "The field is required"
            e.control.update()

alert_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("오류"),
        content=ft.Text("감사합니다 "),
        actions=[
            ft.TextButton("OK", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

channel = ft.RadioGroup( value="tcp", 
                        content=ft.Row([
                            ft.Radio(value="serial", label="시리얼"),
                            ft.Radio(value="tcp", label="TCP/IP"),]))

start_server_button = ft.FilledButton("서버 시작", on_click=start_server, width=140,
            style=ft.ButtonStyle(shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),}))
start_server_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH, alignment=ft.MainAxisAlignment.START,
                          controls=[ start_server_button,])

channel_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH, alignment=ft.MainAxisAlignment.START,
    controls=[ ft.Text("통신채널", width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT), channel,#])
                start_server_button,])

host_ip = ft.TextField( label="호스트 IP", width = LONG_FIELD) #on_blur=validate_required_text_field,
host_port = ft.TextField( label="포트번호", value = 8553, width = SHORT_FIELD) #on_blur=validate_required_text_field,
device_ip = ft.TextField( label="단말 IP", width = LONG_FIELD) #on_blur=validate_required_text_field,

host_ip_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH, alignment=ft.MainAxisAlignment.START,
    controls=[  ft.Text("호스트 IP", width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT), host_ip, 
                ft.Text("포트", width=MID_TITLE_WIDTH, text_align=MID_TITLE_ALIGN, weight=TITLE_WEIGHT), host_port])
device_ip_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH, alignment=ft.MainAxisAlignment.START,
    controls=[  ft.Text("단말 IP", width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT), device_ip,]) 

serial_port = ft.TextField( label="시리얼포트", width = LONG_FIELD
    #on_blur=validate_required_text_field,
    )

serial_speed = ft.Dropdown( label="속도", value=9600, width=SHORT_FIELD,
    options=[   ft.dropdown.Option(4800),
                ft.dropdown.Option(9600),
                ft.dropdown.Option(19200),
                ft.dropdown.Option(38400), ],)

parity = ft.Dropdown( label="패리티", value="N", width=SHORT_FIELD,
    options=[   ft.dropdown.Option("N"),
                ft.dropdown.Option(0),
                ft.dropdown.Option(1),],)

data_size = ft.Dropdown( label="데이터", value=8, width=SHORT_FIELD,
    options=[   ft.dropdown.Option(7),
                ft.dropdown.Option(8), ],)

stopbit = ft.Dropdown( label="스톱비트", value="1", width=SHORT_FIELD,
    options=[   ft.dropdown.Option(1),
                ft.dropdown.Option(2),],)

serial_port_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH,
    alignment=ft.MainAxisAlignment.START,
    controls = [ft.Text("시리얼 포트", width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT), serial_port,
                ft.Text("속도", text_align=MID_TITLE_ALIGN, width=MID_TITLE_WIDTH, weight=TITLE_WEIGHT), serial_speed,
                ft.Text("패리티", text_align=MID_TITLE_ALIGN, width=MID_TITLE_WIDTH, weight=TITLE_WEIGHT), parity, 
                ft.Text("데이터", text_align=MID_TITLE_ALIGN, width=MID_TITLE_WIDTH, weight=TITLE_WEIGHT), data_size, 
                ft.Text("스톱비트", text_align=MID_TITLE_ALIGN, width=MID_TITLE_WIDTH, weight=TITLE_WEIGHT), stopbit,])

serial_options_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH,
    alignment=ft.MainAxisAlignment.START,
    controls = [ft.Text("패리티", text_align=TITLE_ALIGN, width=LEFT_TITLE_WIDTH, weight=TITLE_WEIGHT), parity, 
                ft.Text("데이터", text_align=MID_TITLE_ALIGN, width=MID_TITLE_WIDTH, weight=TITLE_WEIGHT), data_size, 
                ft.Text("스톱비트", text_align=MID_TITLE_ALIGN, width=MID_TITLE_WIDTH, weight=TITLE_WEIGHT), stopbit,])

def update_preview(e):
    #page.update()
    pass

plain_text = ft.TextField(expand=True,on_change=update_preview,
            hint_text=INPUT_HINT, label="전송 데이터(평문)")

request_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH, alignment=ft.MainAxisAlignment.START,
                    controls=[ plain_text,
                                ft.FilledButton("암호화 전송", on_click=request_encryption, width=140,
                                    style=ft.ButtonStyle(shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),})),])

history = ft.TextField(label="기록", expand=True, multiline=True, max_lines=10,on_change=update_preview,value="\n\n\n\n\n\n\n\n\n\n")
history_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH, alignment=ft.MainAxisAlignment.START,
        controls=[  history,
                    ft.FilledButton("삭제", on_click=clear_history, width=140,
                        style=ft.ButtonStyle(shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),})),])

history_column = ft.Column( scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.CENTER, height=400, controls=[ history_row,])

def get_settings():
    return {
        'dirty': True,
        'chan': channel.value, 
        'host_ip': host_ip.value,
        'host_port': host_port.value,
        'device_ip': device_ip.value,
        'serial_port': serial_port.value,
        'serial_speed': serial_speed.value,
        'parity': parity.value,
        'data_size': data_size.value,
        'stopbit': stopbit.value
    }
