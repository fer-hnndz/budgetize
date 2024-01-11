from textual.screen import Screen
from textual.widgets import Header


class MainMenu(Screen):
    CSS_PATH = "css/main_menu.tcss"

    def compose(self):
        self.app.sub_title = "Main Menu"
        yield Header()
