import flet as ft
from controls import *
from comm import *

def main_controls(page):
    return ft.SafeArea(
        ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Divider(thickness=1, color=ft.colors.WHITE, height=5),
                host_ip_row, 
                ft.Divider(thickness=1, height=10),
                channel_row,
                ft.Divider(thickness=1, height=10),
                device_ip_row,
                serial_port_row,
                ft.Divider(thickness=1, height=40),
                request_row,
                history_column,
            ],
            width=ENC_COLUMN_WIDTH
        ),
        expand=True,
    )

def main(page: ft.Page):
    page.title = "(주)위너스엔지니어링 암호화 단말 테스트"
    #page.window_center()
    #page.window_top = 200
    #page.window_left = 400
    page.window_width = ENC_COLUMN_WIDTH
    page.window_height = 720

    host_ip.value = find_host_ip()
    controls = main_controls(page)
    page.add(controls)

    #monitor(serial_thread)

if __name__ == "__main__":
    ft.app(target=main)
