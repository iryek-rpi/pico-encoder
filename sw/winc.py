import flet as ft
import controls as ctr
from control_reference import ControlReference as CR
import comm

def main_controls(page):
    return ft.SafeArea(
        ft.Column(
            controls = [
                ctr.button_row,
                ft.Row(
                    controls=[
                        ctr.og_host,
                        ft.VerticalDivider(width=9, thickness=3),
                        ctr.og_serial,
                        ft.VerticalDivider(width=9, thickness=3),
                        ctr.og_device,
                    ],
                    width=ctr.WINC_WINDOW_WIDTH,
                    alignment=ft.MainAxisAlignment.START,
                ),
            ],
            width=ctr.WINC_WINDOW_WIDTH,
            height=ctr.WINC_WINDOW_HEIGHT,
            alignment=ft.MainAxisAlignment.START,
        ),
        expand=True,
    )

def main(page: ft.Page):
    page.title = "Flet Test"
    page.window_width = ctr.WINC_WINDOW_WIDTH
    page.window_height = ctr.WINC_WINDOW_HEIGHT

    ctr.host_ip.value = comm.find_host_ip()
    ctr.cfg_host_ip.set_value(comm.find_host_ip())
    page.add(main_controls(page))
    CR.add_control_reference("page", page)

if __name__ == "__main__":
    ft.app(target=main)
