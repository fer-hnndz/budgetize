import time

import arrow
from arrow import Arrow
from textual.binding import Binding
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Rule, Select

from core.utils import load_user_data, save_user_data


class AddTransaction(Screen):
    BINDINGS = [
        Binding(
            key="q,Q",
            key_display="Q",
            action="pop_screen",
            description="Cancel Transaction",
        ),
    ]

    def compose(self):
        self.app.sub_title = "Add Transaction"
        yield Header()
        yield Footer()

        yield Label("Account", id="account-label")
        yield Select(
            self._get_account_options(),
            id="account-select",
            allow_blank=False,
            prompt="Select an account",
        )
        yield Label("Transaction Type", id="transaction-type-label")
        yield Select(
            [("Income", "Income"), ("Expense", "Expense")],
            id="transaction-type-select",
            allow_blank=False,
            prompt="Select a transaction type",
        )
        yield Label("Amount", id="amount-label")
        yield Input(
            type="number",
            placeholder="250",
            id="amount-input",
            validators=[Number(minimum=0)],
        )

        today = Arrow.now()
        # TODO: Implement a day and a time picker
        yield Label("Date", id="date-label")
        yield Input(
            placeholder=today.format("M/D/YYYY"),
            id="date-input",
        )

        yield Button("Add Transaction", id="add-transaction-button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add-transaction-button":
            user = load_user_data()
            account_selected: int = self.get_widget_by_id("account-select").value  # type: ignore
            account = user.accounts[int(account_selected)]
            currency = account.currency

            # This can either be Income or Expense
            transaction_type_name = self.get_widget_by_id("transaction-type-select").value  # type: ignore
            amount = self.get_widget_by_id("amount-input").value  # type: ignore

            # Clear fields
            self.get_widget_by_id("amount-input").value = ""  # type: ignore
            self.get_widget_by_id("date-input").value = ""  # type: ignore

            self.app.pop_screen()
            self.app.notify(
                f"You added an {transaction_type_name} of {currency} {amount}"
            )

    def _get_account_options(self):
        user = load_user_data()
        return [(account.name, i) for i, account in enumerate(user.accounts)]
