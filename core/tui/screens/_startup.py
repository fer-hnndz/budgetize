"""Module that defines the startup screen."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, LoadingIndicator


# TODO: Refactor this screen to use new sqlite system
class Startup(Screen):
    """Screen that is shown when the app is opened."""

    CSS_PATH = "css/startup.tcss"

    def compose(self) -> ComposeResult:
        """Called when screen is composed"""
        yield Label("Starting Budgetize...", id="Loading-Label")
        yield LoadingIndicator(id="Loading-Indicator")
