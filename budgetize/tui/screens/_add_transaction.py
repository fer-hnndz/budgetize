"""Module that defines the AddTransaction screen"""

import gettext
from datetime import date as date_func
from traceback import print_exc
from typing import Optional

from arrow import Arrow
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Select

from budgetize._settings_manager import SettingsManager
from budgetize.db import Database
from budgetize.db.orm import Transaction
from budgetize.utils import _

t = gettext.translation(
    "Budgetize", localedir="./budgetize/translations", languages=["es"]
)
_ = t.gettext


class AddTransaction(Screen):
    """Screen that handles adding a new transaction"""

    DB: Database = None  # type: ignore
    BINDINGS = [
        Binding(
            key="q,Q",
            key_display="Q",
            action="pop_screen",
            description=_("Cancel Transaction"),
        ),
    ]

    def __init__(self, transaction: Optional[Transaction] = None) -> None:
        """Creates a new AddTransaction screen"""
        AddTransaction.DB = Database(self.app)
        self.transaction = transaction
        super().__init__()

    def compose(self) -> ComposeResult:
        self.app.sub_title = (
            "Edit Transaction" if self.transaction else "Add Transaction"
        )
        yield Header()
        yield Footer()

        yield Label(_("Account"), id="account-label")
        yield Select(
            self._get_account_options(),
            id="account-select",
            allow_blank=False,
            value=self.transaction.account_id if self.transaction else Select.BLANK,
            prompt="Select an account",
        )
        yield Label(_("Amount"), id="amount-label")
        yield Input(
            type="number",
            placeholder="250",
            id="amount-input",
            value=str(self.transaction.amount) if self.transaction else "",
            validators=[Number(failure_description="Please enter a valid number")],
        )

        today = Arrow.now()

        transaction_date = (
            Arrow.fromtimestamp(self.transaction.timestamp)
            if self.transaction
            else today
        )
        # TODO: Implement a day and a time picker
        yield Label(_("Date"), id="date-label")
        yield Input(
            placeholder=today.format("M/D/YYYY"),
            id="date-input",
            value=transaction_date.format("M/D/YYYY"),
        )

        yield Select(
            self.get_category_select_options(), allow_blank=False, id="category-select"
        )

        yield Label(_("Description"), id="description-label")
        yield Input(
            max_length=255,
            placeholder="Description for your income/expense",
            id="description-input",
            value=self.transaction.description if self.transaction else "",
        )

        lbl = _("Update Transaction") if self.transaction else _("Add Transaction")
        yield Button(lbl, id="add-transaction-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button presses"""

        account_selected: int = self.get_widget_by_id("account-select").value  # type: ignore
        account = self.DB.get_account_by_id(account_selected)
        currency = account.currency

        amount = self.get_widget_by_id("amount-input").value  # type: ignore

        category = self.get_widget_by_id("category-select").value  # type: ignore
        description = self.get_widget_by_id("description-input").value  # type: ignore

        # Attempt to parse the date from the user in M/D/YYYY/
        # If parsing fails, use the current date and time for saving the transaction

        date = Arrow.now()

        try:
            date_strs: list[str] = self.get_widget_by_id("date-input").value.split("/")  # type: ignore
            date_from_input = date_func(
                int(date_strs[2]), int(date_strs[0]), int(date_strs[1])
            )
            date = Arrow.fromdate(date_from_input)

        except Exception:
            print_exc()
            date = Arrow.now()

        # Clear fields
        self.get_widget_by_id("amount-input").value = ""  # type: ignore
        self.get_widget_by_id("date-input").value = ""  # type: ignore

        if self.transaction:
            self.DB.update_transaction(
                transaction_id=self.transaction.id,
                account_id=account.id,
                amount=amount,
                description=description,
                category=category,
                timestamp=date.timestamp(),
            )
            self.app.pop_screen()
            self.app.notify(
                _("Sucessfully updated transaction!"), title=_("Transaction Updated")
            )
            return

        self.DB.add_transaction(
            account_id=account.id,
            amount=amount,
            description=description,
            category=category,
            timestamp=date.timestamp(),
        )

        self.app.pop_screen()
        self.app.notify(
            _("Sucessfully added transaction of {currency} {amount}").format(
                currency=currency, amount=amount
            ),
            title=_("Transaction Added"),
        )

    def _get_account_options(self) -> list[tuple[str, int]]:
        """Returns a list of tuples (name, id) for the TUI to show"""
        return [(account.name, account.id) for account in self.DB.get_accounts()]

    def get_category_select_options(self) -> list[tuple[str, str]]:
        """Returns a list of tuples (name, id) for the TUI to show"""
        categories = []
        for category in SettingsManager().get_categories():
            categories.append((category, category))

        return categories
