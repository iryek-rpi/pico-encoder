'''Flet Expense/Money Concept'''
import flet
from flet import UserControl, Page, Column, Row, Container, Text, padding, alignment
from flet import IconButton, GridView, transform, animation
from flet import LinearGradient

class Expense(UserControl):

    def hover_animation(self, e):
        offset, opacity = 0, 100 if e.data == "true" else 1, 0
        e.control.content.controls[2].offset = transform.Offset(0, offset)
        e.control.content.controls[2].opacity = opacity
        e.control.update()

    def change_icon(e):
        pass

    def icon(self, name, color, selected):
        return IconButton(icon=name, icon_color=color, icon_size=18, selected=selected,on_click=lambda e:self.change_icon(e))

    def MainContainer(self):
        self.main = Container(width=290, height=600, bgcolor='black', border_radius=35, padding=8,)
        self.main_col = Column()

        self.green_container = Container(width=self.main.width, height=self.main.height*0.45, border_radius=30, 
                                         gradient=LinearGradient(begin=alignment.top_left, end=alignment.bottom_right, colors=["#0f766e", "#064e3b"],))
        self.notification = self.icon(icons.NOTIFICATIONS, "white54", True)
        self.hide = self.icon(icons.HIDE_SOURCE, "white54", False)
        self.chat = self.icon(icons.CHAT_ROUNDED, "white54", False)
        self.icon_column = Column(alignment=alignment.center, spacing=5, 
                                  controls=[self.notification, self.hide, self.chat])

        self.innder_green_container = Container(width=self.green_container.width, height=self.green_container.height, 
                            content=Row( spacing=0, controls=[Column(expand=4, controls(padding=20, expand=True, content=
                                                                                        Row(controls=[Column(controls=[
                                                                                            Text("Welcome Back", size=10, color="white70", ),
                                                                                            Text("Line Indent", size=18, weight="bold", ),
                                                                                            Container(padding=padding.only(top=35, bottom=35)),
                                                                                            Text("Total Current Balance", size=10, color="white70", ),
                                                                                            Text("$11,764.28", size=22, weight="bold", ),])]),)],),
                                        Column(expand=1, controls=[Container(padding=padding.only(right=10), expand=True, 
                                                content=Row(alignment=alignment.center, controls=[
                                                   Column(alignment=alignment.center, horizontal_alignment=alignment.center,
                                                          controls=[Column(alignment=alignment.center, horizontal_alignment=alignment.start,
                                                                           controls=[Container(width=40, height=150, bgcolor="white10", border_radius=14, content=self.icon_column,)],)],)],),),],),],),)
        self.grid_transfers = GridView(expand=True, max_extent=150, runs_count=10, spacing=12, run_spacing=5, horizontal=True)
        self.grid_payments = GridView(expand=True, max_extent=150, runs_count=0, spacing=12, run_spacing=5)

        self.main_content_area = Container(width=self.main.width, height=self.main.height*0.50, )


        self.main_col.controls.append(self.green_container)
        self.main.content = self.main_col

        return self.main

    def build(self):
        return Column(
            controls=[self.MainContainer(),]
        )

def start(page: Page):
    page.title='Flet Expense Concept'
    page.horizontal_alignment = alignment.center
    page.vertical_alignment = alignment.center

    app = Expense()
    page.add(app)
    page.update()

if __name__ == '__main__':
    flet.app(target=start)
