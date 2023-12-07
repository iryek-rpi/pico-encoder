import flet as ft
import controls
from controls import *
from control_reference import ControlReference as CR
import comm

def main_controls(page):
    return ft.SafeArea(
        ft.Row(
            controls=[
                OptionGroup("호스트 설정", [custom_host_ip, custom_device_ip, custom_serial_speed, custom_channel]),
                ft.VerticalDivider(width=9, thickness=3),
                OptionGroup("시리얼 통신 설정", [custom_host_ip, custom_device_ip]),
                ft.VerticalDivider(width=9, thickness=3),
                OptionGroup("단말 설정", [custom_host_ip, custom_device_ip]),
            ],
            width=controls.WINC_WINDOW_WIDTH,
            alignment=ft.MainAxisAlignment.START,
        ),
        expand=True,
    )

def main(page: ft.Page):
    page.title = "Flet Test"
    page.window_width = controls.WINC_WINDOW_WIDTH
    page.window_height = controls.WINC_WINDOW_HEIGHT

    host_ip.value = comm.find_host_ip()
    custom_host_ip.set_value(comm.find_host_ip())
    page.add(main_controls(page))
    CR.add_control_reference("page", page)

if __name__ == "__main__":
    ft.app(target=main)
