"""Screen that allows the user to manage their accounts."""

from typing import Generator

from arrow import Arrow
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    TabbedContent,
    TabPane,
)

from budgetize.db import Database


class ManageAccounts(Screen):
    """Screen that allows the user to manage their accounts."""

    DB: Database = None  # type: ignore
    BINDINGS = [Binding("Q,q", "pop_screen", "Back to Main Menu", key_display="Q")]

    def __init__(self) -> None:
        """Creates a new ManageAccounts Screen"""
        ManageAccounts.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        self.app.sub_title = "Manage Accounts"
        yield Header()
        yield Footer()

        with TabbedContent():
            accounts = self.DB.get_accounts()
            for acc in accounts:
                with TabPane(acc.name, id=f"tab-{acc.name.replace(' ', '-')}"):
                    yield Label(f"Balance: {acc.balance}")
                    yield self.get_transactions_table(acc.id)
                    yield Button.error(f"Delete Account", id=f"delete-acc-{acc.id}")

    def generate_accounts_tab(self) -> Generator:
        """Generates the accounts tab including all user accounts"""

        with TabbedContent() as tabs:
            accounts = self.DB.get_accounts()
            for acc in accounts:
                with TabPane(acc.name, id=f"tab-{acc.name.replace(' ', '-')}"):
                    yield Label(f"Balance: {acc.balance}")
                    yield self.get_transactions_table(acc.id)
                    yield Button(f"Delete Account", id=f"delete-acc-{acc.id}")
            return tabs

    def get_transactions_table(self, account: int) -> DataTable:
        """Returns the data table containing the transactions for an account."""

        table: DataTable = DataTable()  # type: ignore
        table.add_columns("Date", "Amount", "Category", "Description")

        now = Arrow.now()
        month = now.format("M")
        year = now.format("YYYY")
        transactions = self.DB.get_monthly_transactions_from_account(
            account, month=month, year=year
        )

        for trans in transactions:
            color = "[green]" if trans.amount > 0 else "[red]"
            date = Arrow.fromtimestamp(trans.timestamp).format("M/D/YYYY")
            table.add_row(
                date, color + str(trans.amount), trans.category, trans.description
            )

        return table

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button push handler"""

        if event.button.id is None:
            return

        if "delete-acc" in event.button.id:
            # Format of btn is delete-acc-{Account.id}

            account_id = int(event.button.id.split("-")[-1])
            account_name = self.DB.get_account_by_id(account_id).name
            self.DB.delete_account(account_id=account_id)
            self.notify(f"{account_name} has been deleted.", title="Account Deleted")
            self.app.pop_screen()
