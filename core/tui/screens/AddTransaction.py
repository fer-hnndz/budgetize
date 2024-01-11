import time

import arrow
from arrow import Arrow
from textual.binding import Binding
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Rule, Select

from core.cli.utils import load_user_data, save_user_data


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
            account_selected = self.get_widget_by_id("account-select").value
            account = user.accounts[account_selected]

            currency = account.currency
            transaction_type = self.get_widget_by_id("transaction-type-select").value
            amount = self.get_widget_by_id("amount-input").value

            # Clear fields
            self.get_widget_by_id("amount-input").value = ""
            self.get_widget_by_id("date-input").value = ""

            self.app.pop_screen()
            self.app.notify(f"You added an {transaction_type} of {currency} {amount}")

    def _get_account_options(self):
        user = load_user_data()
        return [(account.name, i) for i, account in enumerate(user.accounts)]
