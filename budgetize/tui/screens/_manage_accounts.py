"""Screen that allows the user to manage their accounts."""

from arrow import Arrow
from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    ContentSwitcher,
    DataTable,
    Footer,
    Header,
    Label,
    TabbedContent,
    TabPane,
)

from budgetize.db import Database
from budgetize.db.orm import Account


class ManageAccounts(Screen):
    """Screen that allows the user to manage their accounts."""

    DB: Database = None  # type: ignore

    def __init__(self) -> None:
        """Creates a new ManageAccounts Screen"""
        ManageAccounts.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        self.app.sub_title = "Manage Accounts"
        yield Header()
        yield Footer()

        with TabbedContent() as tabs:
            accounts = self.DB.get_accounts()
            for acc in accounts:
                with TabPane(acc.name, id=f"tab-{acc.name}"):
                    yield Label(f"Balance: {acc.balance}")
                    yield self.get_transactions_table(acc.id)

    def refresh_accounts(self) -> None:
        """Refresh the accounts tabs."""

        self.app.pop_screen()
        self.app.push_screen(ManageAccounts())

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
            date = Arrow.fromtimestamp(trans.timestamp).format("M/D/YYYY")
            table.add_row(date, trans.amount, trans.category, trans.description)

        return table
