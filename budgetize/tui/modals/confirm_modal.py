"""Module that defines the ConfirmQuit modal"""

from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from budgetize.utils import _


class ConfirmModal(ModalScreen):
    """Modal that shows up when user is trying to quit the app."""

    CSS_PATH = "css/confirm_quit.tcss"

    def __init__(self, message: str, warn_accept: bool = False) -> None:
        """A modal that asks the user to Accept or Cancel based on the message provided.

        Arguments
        ---------
        message : str
            The message to display to the user.

        warn_accept : bool
            If True, the accept button will be styled as a red button.
        """
        super().__init__()
        self.message = message
        self.warn_accept = warn_accept

    def compose(self) -> ComposeResult:
        """Called when screen is composed"""

        yield Center(
            Label(self.message, id="question"),
            Horizontal(
                Button(
                    _("Accept"),
                    id="yes-button",
                    variant="error" if self.warn_accept else "primary",
                ),
                Button(_("Cancel"), id="no-button", variant="primary"),
                id="horizontal-container",
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed"""

        self.dismiss(event.button.id == "yes-button")
