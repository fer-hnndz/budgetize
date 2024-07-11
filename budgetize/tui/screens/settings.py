import json
import logging
import os
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.types import NoSelection
from textual.widgets import Button, Footer, Header, Label, Select

from budgetize.consts import APP_FOLDER_PATH, AVAILABLE_LANGUAGES, BACKUPS_FOLDER
from budgetize.db.database import Database
from budgetize.settings_manager import SettingsDict, SettingsManager
from budgetize.tui.modals.categories_modal import CategoriesModal
from budgetize.tui.modals.file_selector_modal import FileSelectorModal
from budgetize.tui.modals.message_modal import MessageModal
from budgetize.utils import _, get_select_currencies

logger = logging.getLogger(__name__)


class Settings(Screen):
    DB: Database = None  # type: ignore
    BINDINGS = [
        Binding(
            key="q,Q",
            key_display="Q",
            action="quit_screen",
            description=_("Quit without saving"),
        ),
        Binding(
            key="s,S",
            key_display="S",
            action="save_settings",
            description=_("Save and Quit"),
        ),
    ]

    CSS_PATH = "css/settings.tcss"

    def __init__(self) -> None:
        self.app.sub_title = _("Settings")
        Settings.DB = Database(app=self.app)
        self.manager = SettingsManager()
        super().__init__()

    def action_quit_screen(self) -> None:
        """Action to run when user hits quit screen"""
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        """Composes the Settings Screen"""
        logger.info("Composing Settings Screen...")

        yield Header()
        yield Footer()

        yield Label(_("Language"))
        yield Select(
            id="language-select",
            options=AVAILABLE_LANGUAGES,
            allow_blank=False,
            value=self.manager.get_language(),
        )

        yield Label(_("Main Currency"))
        yield Select(
            id="currency-select",
            options=get_select_currencies(),
            value=self.manager.get_base_currency(),
            allow_blank=False,
        )
        yield Button(_("Manage Categories"), id="categories-btn", variant="primary")
        yield Button(_("Revert Accounts & Transactions from Backup"), id="backup-btn")
        yield Button(_("Export all Budgetize Data"), id="export-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handler"""
        if event.button.id == "categories-btn":
            logger.info("Showing Categories Settings...")
            self.app.push_screen(CategoriesModal())

        if event.button.id == "backup-btn":
            self.app.push_screen(
                FileSelectorModal(
                    BACKUPS_FOLDER,
                    message=_("Select the backup you want to revert to"),
                ),
                self.load_backup,
            )

        if event.button.id == "export-btn":
            self.export_data()

    def export_data(self) -> None:
        """Export all Budgetize data"""
        data: dict[str, dict] = {}

        data["settings"] = self.manager.get_settings_dict()  # type: ignore
        data["database"] = Settings.DB.get_db_as_dict()

        path = os.path.join(APP_FOLDER_PATH, "exported.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        modal = MessageModal(
            _("All data has been exported to {path}").format(path=path)
        )
        self.app.push_screen(modal)

    def load_backup(self, backup: Optional[Path]) -> None:
        """Load a backup file

        Args:
        ----
            backup (str): The path to the backup file

        """
        if backup is None:
            self.notify(
                title=_("Recover From Backup"),
                message=_("No backup selected."),
                severity="warning",
            )
            return

        Settings.DB.revert_from_backup(backup)
        message_modal = MessageModal(
            message=_("Backup loaded successfully.\nPlease restart Budgetize."),
        )
        self.app.push_screen(message_modal)

    def action_save_settings(self) -> None:
        """Action to run when user hits save settings"""
        language = self.get_child_by_id("language-select", expect_type=Select).value
        currency = self.get_child_by_id("currency-select", expect_type=Select).value

        # This should never happen because select are not allowed to be blank
        if isinstance(language, NoSelection) or isinstance(currency, NoSelection):
            return

        language_changed = language != self.manager.get_language()

        # TODO: CREATE A METHOD TO UPDATE THIS
        new_settings: SettingsDict = {
            "language": language,
            "base_currency": currency,
            "categories": self.manager.get_categories(),
        }

        logger.debug("Saving settings: " + str(new_settings))

        if language_changed:
            self.notify(
                _("Close Budgetize to apply the new language."),
                title=_("Language Change"),
            )

        self.manager.save(new_settings)
        logger.info("Settings saved.")
        self.app.pop_screen()
        self.notify(_("Settings saved."), title=_("Settings Changed"))
