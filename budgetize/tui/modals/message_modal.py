"""A Modal that displays the specified message with a button to dismiss it."""

from textual.app import App, ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from budgetize.utils import _


class MessageModal(ModalScreen):
    CSS_PATH = "css/message_modal.tcss"

    def __init__(self, message: str) -> None:
        """
        Creates a Modal that displays the specified message
        with a button to dismiss it.
        """
        self.message = message
        super().__init__()

    def compose(self) -> ComposeResult:
        with Center(id="dialog"):
            yield Label(self.message, id="message")
            yield Button(_("OK"), id="btn-ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handler"""
        self.dismiss(True)
