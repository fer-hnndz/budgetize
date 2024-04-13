"""Main Module that starts the Terminal User Interface (TUI)"""

import logging

from textual.app import App

from budgetize.settings_manager import SettingsManager
from budgetize.tui.screens.create_account import CreateAccount
from budgetize.tui.screens.initial_config import InitialConfig
from budgetize.tui.screens.main_menu import MainMenu
from budgetize.utils import create_logger

create_logger()


class TuiApp(App):
    """App that handles the TUI"""

    def on_mount(self) -> None:
        """Called when the app is mounted"""
        self.title = "Budgetize"
        logging.info("Checking if user has default settings...")
        settings = SettingsManager()

        if settings.is_default_settings():
            logging.info("User has default settings. Redirecting to InitialConfig...")
            self.push_screen(InitialConfig())
        else:
            logging.info("User has custom settings. Redirecting to MainMenu...")
            logging.info("Installing Main Menu screen...")
            self.install_screen(MainMenu(), "main_menu")
            logging.info("Success installing Main Menu Screen")
            logging.info("Installing CreateAccount screen...")
            self.install_screen(CreateAccount(), "create_account")
            logging.info("Succes installing CreateAccount screen")

            logging.info("Showing Main Menu screen...")
            self.push_screen("main_menu")
