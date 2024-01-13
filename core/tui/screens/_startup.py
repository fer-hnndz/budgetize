from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, LoadingIndicator

from core.utils import should_run_initial_config


class Startup(Screen):
    CSS_PATH = "css/startup.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Starting Budgetize...", id="Loading-Label")
        yield LoadingIndicator(id="Loading-Indicator")

    def on_screen_resume(self):
        # await sleep(1.3)

        print("Startup screen is now current screen")
        do_setup = should_run_initial_config()
        print("Initial Config returned: ", do_setup)
        if do_setup:
            self.app.push_screen("initial_config")
        else:
            self.app.push_screen("main_menu")
