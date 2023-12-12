import flet as ft
from pprint import pp

import comm
import w5500.constants as c
import options
from options import OS

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
GROUP_SPACE=4

BUTTON_HEIGHT = 40
BUTTON_BAR_HEIGHT = 60
GROUP_HEIGHT = 480
WINC_WINDOW_WIDTH = GROUP_WIDTH*3+GROUP_SPACE*4 + 10
WINC_WINDOW_HEIGHT = GROUP_HEIGHT + 85 

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

def read_and_apply_options():
    OS.apply_settings(options.load_settings())

def init():
    OS.get(c.HOST_IP).set_value(comm.find_host_ip())
    read_and_apply_options()

class OptionRow(ft.Row):
    def __init__(self, label, control, options_tuple):
        self.option_label = ft.Text(label, width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT)
        if control == ft.TextField:
            self.option_control = ft.TextField(width=LONG_FIELD)
        elif control == ft.Dropdown:
            self.option_control = ft.Dropdown(width=LONG_FIELD,
                                    value=options_tuple[1][options_tuple[0]],
                                    options=[ft.dropdown.Option(option) for option in options_tuple[1]],
                                )
        elif control == ft.RadioGroup:
            self.option_control = ft.RadioGroup(value=options_tuple[0], content = ft.Row([ft.Radio(value=idx, label=option) for idx, option in enumerate(options_tuple[1])]))
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
        self.group_title = ft.Container( 
                                ft.Text(title, weight=TITLE_WEIGHT, size=TITLE_SIZE), 
                                alignment=ft.alignment.center, 
                                bgcolor=ft.colors.BLUE_200, 
                                width=GROUP_WIDTH, 
                                height=GROUP_TITLE_HEIGHT)
        self.options = options
        content = ft.Column(
                        scroll=ft.ScrollMode.HIDDEN, 
                        expand=True, 
                        alignment=ft.MainAxisAlignment.START, 
                        controls=[self.group_title]+self.options, 
                        width=GROUP_WIDTH,
                        height=GROUP_HEIGHT,)
        super().__init__(content=content, width=GROUP_WIDTH, height=GROUP_HEIGHT, bgcolor=ft.colors.BLUE_GREY_100)

button_row = ft.Container( bgcolor=ft.colors.BLUE_GREY_100, width=GROUP_WIDTH*3+GROUP_SPACE*2, height=BUTTON_BAR_HEIGHT,
                content=ft.Row(spacing = 50, width = WINC_WINDOW_WIDTH, height = BUTTON_BAR_HEIGHT, alignment=ft.MainAxisAlignment.CENTER,
                            controls = [
                                ft.FilledButton("단말에서 설정 읽어오기", on_click=read_from_device, width=200, height=BUTTON_HEIGHT,
                                        style=ft.ButtonStyle(shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),})),
                                ft.FilledButton("단말에 설정 저장", on_click=read_from_device, width=200, height=BUTTON_HEIGHT, 
                                        style=ft.ButtonStyle(shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),})),
                            ]))

or_serial_port_list = OptionRow("시리얼 포트 목록:", ft.Dropdown, (0, comm.serial_ports()))
or_serial_port_list.option_control.on_focus = on_portlist_focus

OS.add(c.CHANNEL, OptionRow("통신채널:", ft.RadioGroup, c.CHANNEL_OPTIONS))
OS.add(c.HOST_IP, OptionRow("호스트 IP:", ft.TextField, []))
OS.add(c.HOST_PORT, OptionRow("호스트 포트:", ft.TextField, []))

OS.add(c.SERIAL_PORT, OptionRow("시리얼 포트:", ft.TextField, []))
OS.add(c.SPEED, OptionRow("시리얼 속도:", ft.Dropdown, c.SPEED_OPTIONS))
OS.add(c.PARITY, OptionRow("패리티 비트:", ft.Dropdown, c.PARITY_OPTIONS))
OS.add(c.DATA, OptionRow("데이터 비트:", ft.Dropdown, c.DATA_OPTIONS))
OS.add(c.STOP, OptionRow("스톱 비트:", ft.Dropdown, c.STOP_OPTIONS))

OS.add(c.MY_IP, OptionRow("단말 IP:", ft.TextField, []))
OS.add(c.GATEWAY, OptionRow("게이트웨이:", ft.TextField, []))
OS.add(c.SUBNET, OptionRow("서브넷마스크:", ft.TextField, []))
OS.add(c.PEER_IP, OptionRow("상대 단말 IP:", ft.TextField, []))
OS.add(c.KEY, OptionRow("암호키:", ft.TextField, []))

og_host = OptionGroup("호스트 설정", 
            [OS.get(c.CHANNEL), OS.get(c.HOST_IP), OS.get(c.HOST_PORT)])
og_serial = OptionGroup("시리얼 통신 설정", 
            [OS.get(c.SERIAL_PORT), or_serial_port_list, OS.get(c.SPEED), OS.get(c.PARITY), OS.get(c.DATA), OS.get(c.STOP)])
og_device = OptionGroup("단말 설정", 
            [OS.get(c.MY_IP), OS.get(c.GATEWAY), OS.get(c.SUBNET), OS.get(c.PEER_IP), OS.get(c.KEY)])

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
