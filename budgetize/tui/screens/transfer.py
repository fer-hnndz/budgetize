"""Module that defines the transfer screen between accounts"""

from typing import Optional

from babel.numbers import format_currency
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Rule, Select

from budgetize import CurrencyManager, SettingsManager
from budgetize.db.database import Database
from budgetize.utils import _


class TransferScreen(Screen):
    """Screen used to transfer funds between user accounts"""

    DB: Optional[Database] = None
    CSS_PATH = "css/transfer.tcss"

    def __init__(self) -> None:
        TransferScreen.DB = Database(app=self.app)
        self.app.sub_title = _("Transfer Funds")
        super().__init__()

    def compose(self) -> ComposeResult:
        """Called when screen needs to be composed"""
        yield Header()
        yield Footer()

        with Vertical():
            yield Label(
                "Origin Account New Balance\n[red]1.200,00 HNL",
                id="origin-balance",
            )
            yield Label(
                "Destination Account new Balance\n[green]800.00 US$",
                id="destination-balance",
            )

        with Horizontal():
            with Vertical():
                yield Label(_("Origin Account"), id="origin-label")
                yield Select(self.get_accounts_for_select(), id="origin-select")
                yield Label(_("Amount to Tranfer"), id="transfer-label")
                yield Input(
                    placeholder="100.00",
                    type="number",
                    validators=Number(minimum=1),
                )

            with Vertical():
                yield Label(_("Destination Account"), id="destination-label")
                yield Select(self.get_accounts_for_select(), id="destination-select")

        with Horizontal(id="btn-container"):
            yield Button.success(_("Confirm Transfer"), id="transfer-btn")
            yield Button.error(_("Cancel"), id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button handler"""

        if event.button.id == "cancel-btn":
            self.dismiss(result=None)

    def get_accounts_for_select(self) -> list[tuple[str, int]]:
        """Returns the accounts as tuples of (name, id)"""
        if TransferScreen.DB is None:
            return []

        accounts = TransferScreen.DB.get_accounts()
        account_list = []
        for account in accounts:
            formatted_currency = format_currency(
                TransferScreen.DB.get_account_balance(account.id),
                account.currency,
                locale=SettingsManager().get_locale(),
            )
            name = f"{account.name} | {formatted_currency}"
            account_list.append((name, account.id))
        return account_list
