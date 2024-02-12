"""Module that defines the ConfirmQuit modal"""

from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmQuit(ModalScreen):
    """Modal that shows up when user is trying to quit the app."""

    CSS_PATH = "css/confirm_quit.tcss"

    def compose(self) -> ComposeResult:
        """Called when screen is composed"""

        yield Center(
            Label("Are you sure you want to quit?", id="question"),
            Horizontal(
                Button.error("Yes", id="yes-button"),
                Button("No", id="no-button", variant="primary"),
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed"""

        if event.button.id == "yes-button":
            self.app.exit()
        else:
            self.dismiss()
