from textual.app import App, ComposeResult
from textual.widgets import Label, LoadingIndicator


class Startup(App):
    CSS_PATH = "css/startup.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Starting Budgetize...", name="Loading-Label")
        yield LoadingIndicator(name="Loading-Indicator")
