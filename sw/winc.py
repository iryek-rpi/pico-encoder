import sys
import logging
import flet as ft
import controls as ctr
from control_reference import ControlReference as CR

#logging.basicConfig(filename='winc.log', filemode='w', level=logging.DEBUG)
#logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def setup_custom_logger(name):
    logger = logging.getLogger(name)

    formatter = logging.Formatter(fmt='%(asctime)s:%(module)s/%(funcName)s:%(lineno)d %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.FileHandler('winc.log', mode='w')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)
    return logger

logr = setup_custom_logger('winc')

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
