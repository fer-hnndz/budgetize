"""Main Module that starts the Terminal User Interface (TUI)"""

import logging

from budgetize.consts import VERSION
from budgetize.settings_manager import SettingsManager
from budgetize.tui.screens.create_account import CreateAccount
from budgetize.tui.screens.initial_config import InitialConfig
from budgetize.tui.screens.main_menu import MainMenu
from textual.app import App

logger = logging.getLogger(__name__)


class TuiApp(App):
    """App that handles the TUI"""

    def on_mount(self) -> None:
        """Called when the app is mounted"""
        self.title = f"Budgetize (v{VERSION})"
        logger.info("Checking if user has default settings...")
        settings = SettingsManager()

        if settings.is_default_settings():
            logger.info("User has default settings. Redirecting to InitialConfig...")
            self.push_screen(InitialConfig())
        else:
            logger.info("User has custom settings. Redirecting to MainMenu...")
            logger.info("Installing Main Menu screen...")
            self.install_screen(MainMenu(), "main_menu")
            logger.info("Success installing Main Menu Screen")
            logger.info("Installing CreateAccount screen...")
            self.install_screen(CreateAccount(), "create_account")
            logger.info("Succes installing CreateAccount screen")

            logger.info("Showing Main Menu screen...")
            self.push_screen("main_menu")
