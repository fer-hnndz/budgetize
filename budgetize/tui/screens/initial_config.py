"""Module that defines the InitialConfig screen."""

import gettext
import json
import logging
import os
from pathlib import Path

import babel
from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.types import NoSelection
from textual.widgets import Button, Header, Label, Rule, Select

from budgetize.consts import AVAILABLE_LANGUAGES, TRANSLATIONS_PATH
from budgetize.db.database import Database
from budgetize.settings_manager import SettingsDict, SettingsManager
from budgetize.tui.modals.file_selector_modal import FileSelectorModal
from budgetize.tui.modals.message_modal import MessageModal
from budgetize.utils import get_select_currencies

logger = logging.getLogger(__name__)

# Get default locale, but fallback to English in case of an error.
locale_retrieved = babel.default_locale(category="LANGUAGE")
default_locale = "" if not locale_retrieved else locale_retrieved
try:
    if not default_locale:
        default_locale = "en"
    else:
        default_locale = default_locale.split("_")[0]
except Exception as e:
    logger.error(f"Error getting default locale: {e}")
    default_locale = "en"

t = gettext.translation(
    "budgetize",
    localedir=TRANSLATIONS_PATH,
    languages=[default_locale],
    fallback=True,
)
_ = t.gettext


class InitialConfig(Screen):
    """Screen that handles the initial configuration of the app."""

    CSS_PATH = "css/initial_config.tcss"

    def compose(self) -> ComposeResult:
        """Called when the screen is composed."""
        logger.info("Compose InitialConfig Screen...")
        self.app.sub_title = _("Initial Setup")
        yield Header()

        with Center():
            yield Label(_("Select your Base Currency"), id="currency-label")
            yield Select(
                get_select_currencies(), id="currency-select", allow_blank=False
            )
            yield Label(_("Select a language"), id="language-label")
            yield Select(AVAILABLE_LANGUAGES, id="language-select", allow_blank=False)
            yield Button.success(_("Save"), id="save-button")

            yield Label(
                _("Or import your data from a Budgetize file"), id="import-label"
            )
            yield Rule(line_style="dashed")
            yield Button(_("Import"), id="import-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handler"""
        if event.button.id == "save-button":
            currency = self.get_widget_by_id(
                "currency-select",
                expect_type=Select,
            ).value
            language = self.get_widget_by_id(
                "language-select",
                expect_type=Select,
            ).value

            logger.debug(f"Selected currency: {currency}")
            logger.debug(f"Selected language: {language}")
            # This should never happen at runtime
            if isinstance(language, NoSelection) or isinstance(currency, NoSelection):
                return

            settings = SettingsManager()
            new_settings: SettingsDict = {
                "language": str(language),
                "base_currency": str(currency),
                "categories": settings.get_categories(),
            }
            logger.debug(f"Saving settings: {new_settings}")
            settings.save(new_settings)

            self.show_modal(language)

        if event.button.id == "import-button":

            _ = gettext.translation(
                "budgetize",
                localedir=TRANSLATIONS_PATH,
                languages=[default_locale],
                fallback=True,
            ).gettext

            fs = FileSelectorModal(
                os.path.expanduser("~"), message=_("Select a Budgetize file to import")
            )

            self.app.push_screen(fs, callback=self.process_file_selector_result)

    def process_file_selector_result(self, path: Path) -> None:
        """Process the result of the file selector modal."""
        logging.debug(f"Exported Data selected: {path}")

        _ = gettext.translation(
            "budgetize",
            localedir=TRANSLATIONS_PATH,
            languages=[default_locale],
            fallback=True,
        ).gettext

        if path.suffix != ".budgetize":
            self.app.notify(
                _("Invalid file selected. Please select a [red].budgetize[/red] file.")
            )
            return

        data = self.get_export_data_as_dict(path)
        settings = SettingsManager()
        db = Database(self.app)

        db.populate_from_dict(data["database"])
        settings.save(data["settings"])  # type: ignore

        self.show_modal(language=data["settings"]["language"])

    def get_export_data_as_dict(self, path: Path) -> dict[str, dict]:
        """Create a dictionary from the data in the file."""

        with open(path, "r", encoding="utf-8") as f:
            data: dict[str, dict] = json.load(f)
            return data

    def show_modal(self, language: str) -> None:
        """Shows modal to restart the app to apply language changes."""

        _ = gettext.translation(
            "budgetize",
            localedir=TRANSLATIONS_PATH,
            languages=[language],
            fallback=True,
        ).gettext

        modal = MessageModal(
            message=_(
                "Welcome to Budgetize. Restart the app to apply selected language."
            )
        )

        self.app.push_screen(modal, callback=self.quit_callback)

    def quit_callback(self, data: str = "") -> None:
        """Callback to quit the app. NOTE: PARAMTER IS NOT USED."""
        self.app.exit()
