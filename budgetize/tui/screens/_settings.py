import gettext

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.types import NoSelection
from textual.widgets import Footer, Header, Label, Select

from budgetize import SettingsManager
from budgetize._settings_manager import SettingsDict
from budgetize.consts import AVAILABLE_LANGUAGES
from budgetize.db import Database
from budgetize.utils import _, get_select_currencies


class Settings(Screen):
    DB: Database = None  # type: ignore
    BINDINGS = [
        Binding(
            key="q,Q",
            key_display="Q",
            action="pop_screen",
            description=_("Quit without saving"),
        ),
        Binding(
            key="s,S",
            key_display="S",
            action="save_settings",
            description=_("Save and Quit"),
        ),
    ]

    def __init__(self) -> None:
        self.app.sub_title = _("Settings")
        Settings.DB = Database(app=self.app)
        self.manager = SettingsManager()
        super().__init__()

    def compose(self) -> ComposeResult:
        """Composes the Settings Screen"""

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

    def action_save_settings(self) -> None:
        """Action to run when user hits save settings"""

        language = self.get_child_by_id("language-select", expect_type=Select).value
        currency = self.get_child_by_id("currency-select", expect_type=Select).value

        # This should never happen because select are not allowed to be blank
        if isinstance(language, NoSelection) or isinstance(currency, NoSelection):
            return

        language_changed = language != self.manager.get_language()

        new_settings: SettingsDict = {
            "language": language,
            "base_currency": currency,
            "categories": self.manager.get_categories(),
        }

        if language_changed:
            self.notify(
                _("App will close to apply the new language."),
                title=_("Language Change"),
            )

        self.manager.save(new_settings)
        self.app.pop_screen()
        self.notify(_("Settings saved."), title=_("Settings Changed"))

        if language_changed:
            self.app.exit()
