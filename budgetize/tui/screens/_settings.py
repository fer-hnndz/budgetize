import gettext

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Select, Switch

from budgetize.consts import TRANSLATIONS_PATH
from budgetize.db import Database

t = gettext.translation("budgetize", localedir=TRANSLATIONS_PATH, fallback=True)
_ = t.gettext


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
            action="pop_screen",
            description=_("Save and Quit"),
        ),
    ]

    def __init__(self) -> None:
        self.app.sub_title = _("Settings")
        Settings.DB = Database(app=self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        """Composes the Settings Screen"""

        yield Header()
        yield Footer()

        yield Label(_("Language"))
        yield Select(options=[("English", "us"), ("Español", "es")])
