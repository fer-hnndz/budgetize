"""Main Module that starts the Terminal User Interface (TUI)"""

import os

from textual.app import App

from budgetize._settings_manager import SettingsManager
from budgetize.consts import APP_FOLDER_PATH

from .screens import CreateAccount, InitialConfig, MainMenu


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
