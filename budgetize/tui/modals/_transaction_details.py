from arrow import Arrow
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from budgetize.db import Database
from budgetize.tui.screens._add_transaction import AddTransaction
from budgetize.utils import _


class TransactionDetails(ModalScreen):
    """Modal screen for displaying transaction details."""

    DB: Database = None  # type: ignore
    CSS_PATH = "css/transaction_details.tcss"

    def __init__(self, transaction_id: int, from_manage_accounts: bool = True) -> None:
        """Creates a new TransactionDetails modal."""
        TransactionDetails.DB = Database(self.app)
        self.transaction = self.DB.get_transaction_by_id(transaction_id)
        self.from_manage_accounts = from_manage_accounts

        super().__init__()

    def compose(self) -> ComposeResult:
        """Called when modal needs to be composed."""
        date_str = Arrow.fromtimestamp(self.transaction.timestamp).format("MM/DD/YYYY")

        with Center(id="dialog"):
            yield Label(
                _("Transaction #{transaction_id} Details").format(
                    transaction_id=self.transaction.id
                ),
                id="title",
            )
            yield Label(_("Date: {date_str}").format(date_str=date_str))
            yield Label(
                _("Account: {account_name}").format(
                    account_name=self.DB.get_account_by_id(
                        int(self.transaction.account_id)
                    ).name
                )
            )
            yield Label(_("Amount: {amt}").format(amt=self.transaction.amount))
            yield Label(
                _("Description: {desc}").format(desc=self.transaction.description)
            )
            yield Label(
                _("Category: {category}").format(category=self.transaction.category)
            )
            with Horizontal(id="buttons"):
                yield Button(_("Close"), id="close-button")
                yield Button(_("Edit"), id="edit-button", variant="primary")
                yield Button.error(_("Delete"), id="delete-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button handler"""

        if event.button.id == "close-button":
            self.app.pop_screen()

        if event.button.id == "delete-button":
            self.DB.delete_transaction(self.transaction.id)
            self.app.pop_screen()

            if self.from_manage_accounts:
                self.app.pop_screen()

            self.notify(
                _("The transaction has been successfully deleted."),
                title=_("Transaction Deleted"),
            )

        if event.button.id == "edit-button":
            self.app.pop_screen()
            self.app.push_screen(AddTransaction(self.transaction))
