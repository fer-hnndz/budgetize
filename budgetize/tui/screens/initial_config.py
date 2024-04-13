"""Module that defines the InitialConfig screen."""

import gettext
import logging

import babel
from textual.app import ComposeResult
from textual.screen import Screen
from textual.types import NoSelection
from textual.widgets import Button, Header, Label, Select

from budgetize.consts import AVAILABLE_LANGUAGES, TRANSLATIONS_PATH
from budgetize.settings_manager import SettingsDict, SettingsManager
from budgetize.tui.screens.main_menu import MainMenu
from budgetize.utils import get_select_currencies

# Get default locale, but fallback to English in case of an error.
default_locale = babel.default_locale(category="LANGUAGE")
if not default_locale:
    default_locale = "en"
else:
    default_locale = default_locale.split("_")[0]

t = gettext.translation(
    "budgetize", localedir=TRANSLATIONS_PATH, languages=[default_locale], fallback=True
)
_ = t.gettext


class InitialConfig(Screen):
    """Screen that handles the initial configuration of the app."""

    CSS_PATH = "css/initial_config.tcss"

    def compose(self) -> ComposeResult:
        """Called when the screen is composed."""

        logging.info("Compose InitialConfig Screen...")
        self.app.sub_title = _("Initial Setup")
        yield Header()
        yield Label(_("Select your Base Currency"), id="currency-label")
        yield Select(get_select_currencies(), id="currency-select", allow_blank=False)
        yield Label(_("Select a language"), id="language-label")
        yield Select(AVAILABLE_LANGUAGES, id="language-select", allow_blank=False)
        yield Button.success(_("Save"), id="save-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handler"""

        if event.button.id == "save-button":
            currency = self.get_widget_by_id(
                "currency-select", expect_type=Select
            ).value
            language = self.get_widget_by_id(
                "language-select", expect_type=Select
            ).value

            logging.debug(f"Selected currency: {currency}")
            logging.debug(f"Selected language: {language}")
            # This should never happen at runtime
            if isinstance(language, NoSelection) or isinstance(currency, NoSelection):
                return

            settings = SettingsManager()
            new_settings: SettingsDict = {
                "language": str(language),
                "base_currency": str(currency),
                "categories": settings.get_categories(),
            }
            logging.debug(f"Saving settings: {new_settings}")
            settings.save(new_settings)

            _ = gettext.translation(
                "budgetize",
                localedir=TRANSLATIONS_PATH,
                languages=[language],
                fallback=True,
            ).gettext

            self.app.pop_screen()
            self.app.install_screen(MainMenu(), "main_menu")
            self.app.push_screen("main_menu")
            self.app.notify(
                _("Welcome to Budgetize. Restart the app to apply selected language."),
                title=_("Settings Applied"),
            )
