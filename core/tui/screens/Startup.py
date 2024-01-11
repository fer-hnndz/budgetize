from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, LoadingIndicator
from core.cli.utils import should_run_initial_config
from textual.events import Event, Ready
from textual import on


class Startup(Screen):
    CSS_PATH = "css/startup.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Starting Budgetize...", id="Loading-Label")
        yield LoadingIndicator(id="Loading-Indicator")

    @on(Ready)
    def on_ready(self):
        print("APP IS READY!!!")
        if should_run_initial_config():
            self.app.push_screen("initial_config")
        else:
            self.app.push_screen("main_menu")
