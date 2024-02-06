"""Module that defines the AddTransaction screen"""

from datetime import date as date_func
from traceback import print_exc

from arrow import Arrow
from textual.binding import Binding
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Select

from budgetize.consts import DEFAULT_CATEGORIES
from budgetize.db import Database
from budgetize.db.orm import Transaction


class AddTransaction(Screen):
    """Screen that handles adding a new transaction"""

    DB: Database = None  # type: ignore
    BINDINGS = [
        Binding(
            key="q,Q",
            key_display="Q",
            action="pop_screen",
            description="Cancel Transaction",
        ),
    ]

    def __init__(self) -> None:
        """Creates a new AddTransaction screen"""
        AddTransaction.DB = Database(self.app)
        super().__init__()

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

        yield Select(
            self.get_category_select_options(), allow_blank=False, id="category-select"
        )

        yield Label("Description", id="description-label")
        yield Input(
            max_length=255,
            placeholder="Description for your income/expense",
            id="description-input",
        )
        yield Button("Add Transaction", id="add-transaction-button")

    def on_button_pressed(self, event: Button.Pressed):
        """Handles button presses"""

        if event.button.id == "add-transaction-button":
            account_selected: int = self.get_widget_by_id("account-select").value  # type: ignore
            account = self.DB.get_account_by_id(account_selected)
            currency = account.currency

            # This can either be Income or Expense
            transaction_type_name = self.get_widget_by_id("transaction-type-select").value  # type: ignore # pylint: disable=line-too-long
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

            transaction = Transaction(
                account_id=account.id,
                amount=amount,
                description=description,
                category=category,
                timestamp=date.timestamp(),
            )
            self.DB.add_transaction(transaction)
            self.app.pop_screen()
            self.app.notify(
                f"You added an {transaction_type_name} of {currency} {amount}"
            )

    def _get_account_options(self) -> list[tuple[str, int]]:
        """Returns a list of tuples (name, id) for the TUI to show"""
        return [(account.name, account.id) for account in self.DB.get_accounts()]

    def get_category_select_options(self) -> list[tuple[str, str]]:
        categories = []
        for category in DEFAULT_CATEGORIES:
            categories.append((category, category))

        return categories
