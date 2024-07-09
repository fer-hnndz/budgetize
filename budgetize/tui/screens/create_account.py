"""Module that defines the CreateAccount screen."""

import logging

from budgetize.db.database import Database
from budgetize.tui.modals.error_modal import ErrorModal
from budgetize.utils import _, get_select_currencies
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Select

logger = logging.getLogger(__name__)


class CreateAccount(Screen):
    """Screen that allows the user to create a new account."""

    CSS_PATH = "css/create_account.tcss"

    DB: Database = None  # type: ignore
    BINDINGS = [
        Binding(
            key="c,C",
            key_display="C",
            action="pop_screen",
            description=_("Cancel"),
        ),
    ]

    def __init__(self) -> None:
        """Creates a new CreateAccount Screen"""
        CreateAccount.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        """Called when the screen is composed."""
        logger.info("Composing CreateAccount Screen...")
        self.app.sub_title = _("Create Account")
        yield Header()
        yield Footer()

        yield VerticalScroll(
            Grid(
                # Place them in this way because grids are filled in row-order
                Label(_("Account Currency"), id="currency-label"),
                Label(_("Account Name"), id="name-label"),
                Select(
                    get_select_currencies(),
                    id="currency-select",
                    allow_blank=False,
                ),
                Input(placeholder=_("Bank Account"), id="account-name-input"),
            ),
            Label(_("Starting Balance"), id="balance-label"),
            Input(
                type="number",
                placeholder="250",
                id="balance-input",
                validators=[
                    Number(
                        minimum=0,
                        failure_description=_("Initial Balance must be atleast zero."),
                    ),
                ],
            ),
            Horizontal(
                Button.success(_("Create Account"), id="create-account-button"),
                Button.error(_("Cancel"), id="cancel-button"),
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handlers"""
        if event.button.id == "create-account-button":
            name: str = self.get_widget_by_id("account-name-input").value  # type: ignore
            currency: str = self.get_widget_by_id("currency-select").value  # type: ignore
            starting_balance: float = self.get_widget_by_id("balance-input").value  # type: ignore

            logger.debug(f"Creating Account: {name} {currency} {starting_balance}")

            if self.DB.account_name_exists(name):
                logger.warning("Account Name already exists! Showing error")
                self.app.push_screen(
                    ErrorModal(
                        _("Account Name already Exists"),
                        traceback_msg=_(
                            "You cannot have 2 accounts with the same name!",
                        ),
                    ),
                )
                return

            self.DB.add_account(
                name=name,
                currency=currency,
                starting_balance=starting_balance,
            )

            self.notify(_("Account created successfully."), title="Account Created")
            self.get_widget_by_id("account-name-input").value = ""  # type: ignore
            self.get_widget_by_id("balance-input").value = ""  # type: ignore
            self.app.pop_screen()
        else:
            # Clear the input fields
            self.get_widget_by_id("account-name-input").value = ""  # type: ignore
            self.get_widget_by_id("balance-input").value = ""  # type: ignore
            self.app.pop_screen()
