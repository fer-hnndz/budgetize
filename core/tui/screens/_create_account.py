from textual.binding import Binding
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Select

from core.accounts import Account, AccountType
from core.consts import CURRENCY_SYMBOLS
from core.utils import load_user_data, save_user_data


class CreateAccount(Screen):
    BINDINGS = [
        Binding(key="q,Q", key_display="Q", action="pop_screen", description="Cancel"),
    ]

    def compose(self):
        self.app.sub_title = "Create Account"
        yield Header()
        yield Footer()
        yield Label("Base Currency", id="currency-label")
        yield Select(
            self.get_currency_choices(), id="currency-select", allow_blank=False
        )
        yield Label("Account Name", id="name-label")
        yield Input(placeholder="Bank Account", id="account-name-input")
        yield Label("Starting Balance", id="balance-label")
        yield Input(
            type="number",
            placeholder="250",
            id="balance-input",
            validators=[
                Number(
                    minimum=0,
                    failure_description="Initial Balance must be atleast zero.",
                )
            ],
        )
        yield Label("Account Type", id="account-type-label")
        yield Select(self.get_account_type_choices(), id="account-type-select")
        yield Button.success("Create Account", id="create-account-button")
        yield Button.error("Cancel", id="cancel-button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "create-account-button":
            user = load_user_data()
            name: str = self.get_widget_by_id("account-name-input").value  # type: ignore
            currency: str = self.get_widget_by_id("currency-select").value  # type: ignore
            balance: float = self.get_widget_by_id("balance-input").value  # type: ignore
            account_type_name: str = self.get_widget_by_id("account-type-select").value  # type: ignore

            user.accounts.append(
                Account(
                    account_type=AccountType[account_type_name.upper()],
                    name=name,
                    currency=currency,
                    balance=balance,
                    transactions=[],
                )
            )

            save_user_data(user)
            self.app.pop_screen()
            self.notify("Account created successfully.", title="Account Created")

        elif event.button.id == "cancel-button":
            self.get_widget_by_id("account-name-input").value = ""  # type: ignore
            self.get_widget_by_id("balance-input").value = ""  # type: ignore
            self.app.pop_screen()

    def get_currency_choices(self) -> list:
        res = []
        for symbol in CURRENCY_SYMBOLS:
            res.append((symbol, symbol))

        return res

    def get_account_type_choices(self) -> list:
        res = []
        for acc in AccountType:
            res.append((acc.name.capitalize(), acc.name.capitalize()))

        return res
