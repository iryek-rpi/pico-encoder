import flet as ft

def main(page: ft.Page):
    def dropdown_changed(e):
        t.value = f"Dropdown changed to {dd.value}"
        page.update()

    t = ft.Text()
    dd = ft.Dropdown(color=ft.colors.RED_500,
                on_change=dropdown_changed,
                options=[
                    ft.dropdown.Option("Red"),
                    ft.dropdown.Option("Green"),
                    ft.dropdown.Option("Blue"),
                ],
                width=200,
            )

    cc = ft.Container(
            bgcolor=ft.colors.RED_500,
            content=dd    )
    page.add(cc, t)

ft.app(target=main)