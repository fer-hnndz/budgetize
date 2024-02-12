from arrow import Arrow
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from budgetize.db import Database
from budgetize.db.orm import Transaction


class TransactionDetails(ModalScreen):
    """Modal screen for displaying transaction details."""

    DB: Database = None  # type: ignore
    CSS_PATH = "css/transaction_details.tcss"

    def __init__(self, transaction_id: int) -> None:
        """Creates a new TransactionDetails modal."""
        TransactionDetails.DB = Database(self.app)
        self.transaction = self.DB.get_transaction_by_id(transaction_id)
        super().__init__()

    def compose(self) -> ComposeResult:
        """Called when modal needs to be composed."""

        date_str = Arrow.fromtimestamp(self.transaction.timestamp).format("MM/DD/YYYY")

        with Center(id="dialog"):
            yield Label(f"Transaction #{self.transaction.id} Details", id="title")
            yield Label(f"Date: {date_str}")
            yield Label(
                f"Account: {self.DB.get_account_by_id(int(self.transaction.account_id)).name}"
            )
            yield Label(f"Amount: {self.transaction.amount}")
            yield Label(f"Description: {self.transaction.description}")
            yield Label(f"Category: {self.transaction.category}")
            with Horizontal(id="buttons"):
                yield Button("Close", id="close-button")
                yield Button("Edit", id="edit-button", variant="primary")
                yield Button.error("Delete", id="delete-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button handler"""

        if event.button.id == "close-button":
            self.app.pop_screen()
