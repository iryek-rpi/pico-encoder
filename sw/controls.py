import flet as ft

ENC_COLUMN_WIDTH = 1000
LEFT_TITLE_WIDTH = 80
MID_TITLE_WIDTH = 55 
TITLE_ALIGN = ft.TextAlign.CENTER
MID_TITLE_ALIGN = ft.TextAlign.END
TITLE_WEIGHT = ft.FontWeight.BOLD
LONG_FIELD = 180
SHORT_FIELD = 100
MID_FIELD = 120

channel = ft.RadioGroup( value="serial", content=ft.Row([
            ft.Radio(value="serial", label="시리얼"),
            ft.Radio(value="tcp", label="TCP/IP"),]))

channel_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH,
    alignment=ft.MainAxisAlignment.START,
    controls=[ ft.Text("통신채널", width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT), channel, ])

ip = ft.TextField( label="IP 주소", width = LONG_FIELD
    #on_blur=validate_required_text_field,
    )

port = ft.TextField( label="Port", width = SHORT_FIELD
    #on_blur=validate_required_text_field,
    )

ip_row = ft.Row( spacing = 5, width = ENC_COLUMN_WIDTH,
    alignment=ft.MainAxisAlignment.START,
    controls=[  ft.Text("IP 주소", width=LEFT_TITLE_WIDTH, text_align=TITLE_ALIGN, weight=TITLE_WEIGHT), ip, 
                ft.Text("Port", width=MID_TITLE_WIDTH, text_align=MID_TITLE_ALIGN, weight=TITLE_WEIGHT), port])

serial_port = ft.TextField( label="시리얼포트", width = LONG_FIELD
    #on_blur=validate_required_text_field,
    )

serial_speed = ft.Dropdown( label="속도", value="9600", width=SHORT_FIELD,
    options=[   ft.dropdown.Option("4800"),
                ft.dropdown.Option("9600"),
                ft.dropdown.Option("19200"),
                ft.dropdown.Option("38400"), ],)

parity = ft.Dropdown( label="패리티", value="N", width=SHORT_FIELD,
    options=[   ft.dropdown.Option("N"),
                ft.dropdown.Option("Even"),
                ft.dropdown.Option("Odd"),],)

data_size = ft.Dropdown( label="데이터", value="8", width=SHORT_FIELD,
    options=[   ft.dropdown.Option("7"),
                ft.dropdown.Option("8"), ],)

stopbit = ft.Dropdown( label="스톱비트", value="1", width=SHORT_FIELD,
    options=[   ft.dropdown.Option("1"),
                ft.dropdown.Option("2"),],)

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