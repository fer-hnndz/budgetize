"""Module that defines the modal that shows up when an error occurs in the app."""

import pyperclip
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ErrorModal(ModalScreen):
    CSS_PATH = "css/error_modal.tcss"

    def __init__(self, title: str, traceback_msg: str) -> None:
        super().__init__()

        self.title = title
        self.traceback_msg = traceback_msg

        if self.title is None or self.traceback_msg is None:
            raise ValueError("Both title and traceback_msg must be provided.")

    def compose(self) -> ComposeResult:
        """Called when screen needs to be composed."""

        # Should not happen but mypy complains
        if (self.title is None) or (self.traceback_msg is None):
            return

        with Center(id="center-modal"):
            yield Label(self.title, id="title-str")
            yield Label(self.traceback_msg, id="traceback-str")

            with Horizontal(id="horizontal-modal"):
                yield Button("Copy to clipboard", id="copy-btn", variant="primary")
                yield Button.error("Close", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handler"""

        if event.button.id == "close-btn":
            self.dismiss()

        elif event.button.id == "copy-btn":

            if self.title is None or self.traceback_msg is None:
                return
            pyperclip.copy(self.title + "\n\n" + self.traceback_msg)
            self.dismiss()
