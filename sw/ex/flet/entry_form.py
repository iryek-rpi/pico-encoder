import flet as ft

def main_controls(page):
    gender = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="female", label="Female"),
                ft.Radio(value="male", label="Male"),
                ft.Radio(value="not_specified", label="Not specified"),
            ]
        )
    )

    choice_of_instrument = ft.Dropdown(
        label="Choice of instrument",
        options=[
            ft.dropdown.Option("Piano"),
            ft.dropdown.Option("Violin"),
            ft.dropdown.Option("Guitar"),
        ],
    )

    def update_preview(e):
        """
        Updates the RHS(markdown/preview) when the content of the textfield changes.
        :param e: the event that triggered the function
        """
        page.update()


    plain_text = ft.TextField(
            expand=True,
            on_change=update_preview,
            value="전송할 데이터를 입력하세요"
            #label="전송할 데이터를 입력하세요"
        )
    def request_encryption(e):
        dlg.content.value = plain_text.value
        plain_text.hint_text = plain_text.value
        plain_text.value = ""
        e.control.page.dialog = dlg
        dlg.open = True
        e.control.page.update()
        print(plain_text.value)

    def clear_history(e):
        e.control.page.dialog = dlg
        dlg.open = True
        e.control.page.update()
        print("기록 삭제됨")

    def close_dlg(e):
        dlg.open = False
        e.control.page.update()

    def validate_required_text_field(e):
        if e.control.value == "":
            e.control.error_text = "The field is required"
            e.control.update()

    dlg = ft.AlertDialog(
        # modal=True,
        # title=ft.Text("Form submitted"),
        content=ft.Text("감사합니다 "),
        actions=[
            ft.TextButton("OK", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )
    
    submit = ft.FilledButton("삭제", on_click=clear_history),

    request_row = ft.Row(
        spacing = 5,
        width = 500,
        alignment=ft.MainAxisAlignment.START,
        controls=[
            plain_text,
            ft.FilledButton("암호화 전송", on_click=request_encryption, width=120,
                style=ft.ButtonStyle(
                    shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),})),
        ]
    )
    history_row = ft.Row(
        spacing = 5,
        width = 500,
        alignment=ft.MainAxisAlignment.START,
        controls=[
            ft.TextField(
                label="기록",
                expand=True,
                #disabled=True,
                multiline=True,
                max_lines=5,
                on_change=update_preview,
                value="\n\n\n\n\n"
            ),
            ft.FilledButton("삭제", on_click=clear_history, width=120,
                style=ft.ButtonStyle(
                    shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2),})),
        ]
    )
    history_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.CENTER,
        height=200,
        controls=[
            history_row,
        ]
    )

    return ft.SafeArea(
        ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.TextField(
                    label="First name",
                    keyboard_type=ft.KeyboardType.NAME,
                    on_blur=validate_required_text_field,
                ),
                ft.TextField(
                    label="Last name",
                    keyboard_type=ft.KeyboardType.NAME,
                    on_blur=validate_required_text_field,
                ),
                ft.TextField(
                    label="Email",
                    keyboard_type=ft.KeyboardType.EMAIL,
                    on_blur=validate_required_text_field,
                ),
                ft.TextField(
                    label="Age",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    on_blur=validate_required_text_field,
                ),
                ft.Text("Gender:"),
                gender,
                ft.Divider(thickness=1),
                choice_of_instrument,
                ft.Text("Pick days for classes:"),
                request_row,
                history_column,
            ],
            width=560
        ),
        expand=True,
    )


def main(page: ft.Page):
    page.title = "(주)위너스엔지니어링 암호화 단말 테스트"
    #page.window_center()
    page.window_top = 200
    page.window_left = 400
    page.window_width = 600
    page.window_height = 800
    page.add(main_controls(page))


if __name__ == "__main__":
    ft.app(target=main)
