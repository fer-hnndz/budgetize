"""Main Module that starts the Terminal User Interface (TUI)"""

from textual.app import App

from budgetize._settings_manager import SettingsManager
from budgetize.tui.screens.create_account import CreateAccount
from budgetize.tui.screens.initial_config import InitialConfig
from budgetize.tui.screens.main_menu import MainMenu


class TuiApp(App):
    """App that handles the TUI"""

    def on_mount(self) -> None:
        """Called when the app is mounted"""

        self.title = "Budgetize"
        settings = SettingsManager()

        if settings.is_default_settings():
            self.push_screen(InitialConfig())
        else:
            self.install_screen(MainMenu(), "main_menu")
            self.install_screen(CreateAccount(), "create_account")
            self.push_screen("main_menu")
