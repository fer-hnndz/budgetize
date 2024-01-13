from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Select

import core.consts as consts
from core.utils import save_user_data


class InitialConfig(Screen):
    CSS_PATH = "css/initial_config.tcss"

    def compose(self) -> ComposeResult:
        self.app.sub_title = "Initial Setup"
        yield Header()
        yield Label("Select your base currency", id="currency-label")
        yield Select(
            self.get_currency_choices(), id="currency-select", allow_blank=False
        )
        yield Label("Enter your name", id="name-label")
        yield Input(placeholder="Name", id="name-input")
        yield Button.success("Save", id="save-button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save-button":
            name: str = self.get_widget_by_id("name-input").value  # type:ignore
            currency: str = self.get_widget_by_id(
                "currency-select"
            ).value  # type:ignore
            # user = User(name=name, base_currency=currency, accounts=[])
            # save_user_data(user)

            self.app.pop_screen()
            self.app.push_screen("main_menu")
            self.app.notify(f"Welcome to Budgetize, {name}", title="User Created")

    def get_currency_choices(self) -> list[tuple[str, str]]:
        res = []
        for symbol in consts.CURRENCY_SYMBOLS:
            res.append((symbol, symbol))

        return res
