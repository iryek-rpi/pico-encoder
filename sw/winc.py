import flet as ft
import controls as ctr
from control_reference import ControlReference as CR

def main_controls(page):
    ctr.init()
    return ft.SafeArea(
        ft.Column(
            controls = [
                ctr.button_row,
                ft.Row( controls=[ ctr.og_host, ctr.og_serial, ctr.og_device,],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=ctr.GROUP_SPACE,
                ),
            ],
            height=ctr.WINC_WINDOW_HEIGHT,
            alignment=ft.MainAxisAlignment.START,
            spacing=ctr.GROUP_SPACE
        ),
        expand=True,
    )

def main(page: ft.Page):
    page.title = "Flet Test"
    page.window_width = ctr.WINC_WINDOW_WIDTH
    page.window_height = ctr.WINC_WINDOW_HEIGHT

    page.add(main_controls(page))
    CR.add_control_reference("page", page)

if __name__ == "__main__":
    ft.app(target=main)
