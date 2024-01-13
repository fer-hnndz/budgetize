from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Rule, Tabs

from core.db import Database
from core.utils import load_user_data


class MainMenu(Screen):
    CSS_PATH = "css/main_menu.tcss"
    BINDINGS = [
        Binding(
            key="n,N",
            key_display="N",
            action="push_screen('add_transaction')",
            description="Add Transaction",
        ),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()

    def compose(self) -> ComposeResult:
        self.app.sub_title = "Main Menu"
        yield Header()
        yield Footer()
        yield Label("Accounts", id="accounts-label")
        yield Rule(orientation="horizontal", line_style="heavy")
        yield Horizontal(
            DataTable(id="accounts-table"),
            Vertical(
                Label("Income this Month\n[green]L. 250.00[/green]"),
                Label("Balance\n[green]L. 250.00[/green]"),
                Label("Expenses this Month\n[red]L. 250.00[/red]"),
            ),
        )
        yield Horizontal(
            Button("Create Account", id="create-account-button"),
            Button("Manage Accounts"),
        )
        yield Label("Recent Transactions", id="recent-transactions-label")

        # Generate last 5 transactions
        # TODO: Replace the place holders
        yield DataTable(id="recent-transactions-table")

        yield Rule(orientation="horizontal")

    def on_mount(self):
        self._update_account_tables()
        self._update_recent_transactions_table()

    def _update_recent_transactions_table(self) -> None:
        # TODO: Implement this method based on users' transactions

        table: DataTable = self.get_widget_by_id("recent-transactions-table")  # type: ignore
        table.clear(columns=True)
        table.add_columns("Account", "Amount", "Date", "Category")
        table.add_row("Wallet", "[red] HNL 250.00", "2021-01-01", "Food")
        table.add_row("Wallet", "[green] HNL 250.00", "2021-01-01", "Income")

    def _update_account_tables(self) -> None:
        table: DataTable = self.get_widget_by_id("accounts-table")  # type: ignore
        table.clear(columns=True)
        table.add_columns("Account Name", "Account Type", "Balance", "Currency")

        for acc in self.db.get_accounts():
            table.add_row(
                acc.name, acc.account_type.name.capitalize(), acc.balance, acc.currency
            )

    def on_screen_resume(self):
        print("Main Menu is now current")
        self._update_account_tables()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "create-account-button":
            self.app.push_screen("create_account")
        if event.button.id == "manage-accounts-button":
            self.app.push_screen("manage_accounts")
