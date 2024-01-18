"""Main Module that starts the Terminal User Interface (TUI)"""

from textual.app import App

from .screens import AddTransaction, CreateAccount, InitialConfig, MainMenu, Startup


class TuiApp(App):
    """App that handles the TUI"""

    def on_mount(self):
        """Called when the app is mounted"""
        self.title = "Budgetize"
        self.install_screen(Startup(), "startup")
        self.install_screen(InitialConfig(), "initial_config")
        self.install_screen(MainMenu(), "main_menu")
        self.install_screen(CreateAccount(), "create_account")
        self.install_screen(AddTransaction(), "add_transaction")
        # self.install_screen(ManageAccounts(), "manage_accounts") # Create a new instance every time it needs to be shown
        self.push_screen("main_menu")
