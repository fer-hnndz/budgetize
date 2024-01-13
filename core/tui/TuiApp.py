from textual.app import App, ComposeResult
from textual.message import Message

from .screens import AddTransaction, CreateAccount, InitialConfig, MainMenu, Startup


class TuiApp(App):
    def on_mount(self):
        self.title = "Budgetize"
        self.install_screen(Startup(), "startup")
        self.install_screen(InitialConfig(), "initial_config")
        self.install_screen(MainMenu(), "main_menu")
        self.install_screen(CreateAccount(), "create_account")
        self.install_screen(AddTransaction(), "add_transaction")
        self.push_screen("main_menu")
