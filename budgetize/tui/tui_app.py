"""Main Module that starts the Terminal User Interface (TUI)"""

from textual.app import App

from .screens import AddTransaction, CreateAccount, MainMenu, Startup


class TuiApp(App):
    """App that handles the TUI"""

    def on_mount(self) -> None:
        """Called when the app is mounted"""
        self.title = "Budgetize"
        self.install_screen(Startup(), "startup")
        self.install_screen(MainMenu(), "main_menu")
        self.install_screen(CreateAccount(), "create_account")
        self.install_screen(AddTransaction(), "add_transaction")
        self.push_screen("main_menu")
