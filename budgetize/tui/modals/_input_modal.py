from typing import Optional

from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.validation import Number
from textual.widgets import Button, Input, Label

from budgetize.utils import _


class InputModal(ModalScreen[str]):
    """Modal that allows user to enter an input."""

    CSS_PATH = "css/input_modal.tcss"

    def __init__(
        self,
        prompt: str,
        only_numbers: bool = False,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_blank: bool = False,
        validators: list = [],
    ):
        """Creates a new input modal with the specified prompt.

        When `only_numbers` is set to `True` the Input will only allow for numbers.
        -   Edit min and max values to set the range of numbers allowed.
        -   This is only considered when `only_numbers` is set to `True`.
        When `allow_blank` is set to `True` the Input will allow for an empty string.
        """

        self.prompt = prompt
        self.only_numbers = only_numbers
        self.allow_blank = allow_blank
        self.validators = validators

        if only_numbers:
            self.validators.append(Number(minimum=min_value, maximum=max_value))
        super().__init__()

    def compose(self) -> ComposeResult:
        """Called when screen is built."""

        required: str = "[bold red]*[/bold red]" if not self.allow_blank else ""

        with Center(id="center"):
            yield Label(f"[bold][white]{self.prompt}{required}", id="prompt")
            yield Input(
                validators=self.validators,
                valid_empty=self.allow_blank,
                id="modal-input",
            )

            with Horizontal(id="horizontal"):
                yield Button(
                    _("Done"),
                    id="done-btn",
                    variant="primary",
                    disabled=not self.allow_blank,
                )

                if self.allow_blank:
                    yield Button.error(_("Cancel"), id="cancel-btn")

    def action_done_button_clicked(self) -> None:
        """Called when the done button is clicked."""
        center_container = self.get_child_by_id(id="center", expect_type=Center)
        input_widget = center_container.get_child_by_id(
            id="modal-input", expect_type=Input
        )
        self.dismiss(input_widget.value)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Called when an Input widget is changed"""

        # Don't disable the button if the input is allowed to be blank
        if self.allow_blank:
            return

        center_container = self.get_child_by_id(id="center", expect_type=Center)
        horizontal_container = center_container.get_child_by_id(
            id="horizontal", expect_type=Horizontal
        )
        confirm_button = horizontal_container.get_child_by_id(
            "done-btn", expect_type=Button
        )

        if event.input.value:
            confirm_button.disabled = False

        else:
            confirm_button.disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed."""

        if event.button.id == "cancel-btn":
            self.dismiss("")
        self.action_done_button_clicked()
