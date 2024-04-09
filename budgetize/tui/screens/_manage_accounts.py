"""Screen that allows the user to manage their accounts."""

import gettext
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

from budgetize.consts import TRANSLATIONS_PATH
from budgetize.db import Database
from budgetize.tui.modals import TransactionDetails
from budgetize.utils import _


class ManageAccounts(Screen):
    """Screen that allows the user to manage their accounts."""

    DB: Database = None  # type: ignore
    BINDINGS = [Binding("Q,q", "pop_screen", _("Back to Main Menu"), key_display="Q")]

    def __init__(self) -> None:
        """Creates a new ManageAccounts Screen"""
        ManageAccounts.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        self.app.sub_title = _("Manage Accounts")
        yield Header()
        yield Footer()

        with TabbedContent():
            accounts = self.DB.get_accounts()
            for acc in accounts:
                with TabPane(acc.name, id=f"tab-{acc.name.replace(' ', '-')}"):
                    yield Label(_("Balance: {balance}").format(balance=acc.balance))
                    yield self.get_transactions_table(acc.id)
                    yield Button.error(_("Delete Account"), id=f"delete-acc-{acc.id}")

    def generate_accounts_tab(self) -> Generator:
        """Generates the accounts tab including all user accounts"""

        with TabbedContent() as tabs:
            accounts = self.DB.get_accounts()
            for acc in accounts:
                with TabPane(acc.name, id=f"tab-{acc.name.replace(' ', '-')}"):
                    yield Label(_("Balance: {balance}").format(balance=acc.balance))
                    yield self.get_transactions_table(acc.id)
                    yield Button(_("Delete Account"), id=f"delete-acc-{acc.id}")
            return tabs

    def get_transactions_table(self, account: int) -> DataTable:
        """Returns the data table containing the transactions for an account."""

        table: DataTable = DataTable(id=f"management-table-{str(account)}")  # type: ignore
        table.add_columns(_("Date"), _("Amount"), _("Category"), _("Description"))

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
                date,
                color + str(trans.amount),
                trans.category,
                trans.description,
                key=trans.id,
            )

        return table

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Cell selection handler"""

        selected_cell = event.coordinate.row
        current_row = 0
        for row in event.data_table.rows:
            if current_row == selected_cell and row.value is not None:
                details_screen = TransactionDetails(
                    int(row.value), from_manage_accounts=True
                )
                self.app.push_screen(details_screen)
                break
            current_row += 1

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button push handler"""

        if event.button.id is None:
            return

        if "delete-acc" in event.button.id:
            # Format of btn is delete-acc-{Account.id}

            account_id = int(event.button.id.split("-")[-1])
            account_name = self.DB.get_account_by_id(account_id).name
            self.DB.delete_account(account_id=account_id)
            self.notify(
                _("{account_name} has been deleted.").format(account_name=account_name),
                title=_("Account Deleted"),
            )
            self.app.pop_screen()
