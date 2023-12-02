from datetime import datetime

import flet as ft
import comm

ENC_COLUMN_WIDTH = 1000
LEFT_TITLE_WIDTH = 80
MID_TITLE_WIDTH = 60 
TITLE_ALIGN = ft.TextAlign.CENTER
MID_TITLE_ALIGN = ft.TextAlign.END
TITLE_WEIGHT = ft.FontWeight.BOLD
LONG_FIELD = 180
SHORT_FIELD = 100
MID_FIELD = 120
INPUT_HINT = "전송할 데이터를 입력하세요"

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

channel = ft.RadioGroup( value="tcp", content=ft.Row([
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
