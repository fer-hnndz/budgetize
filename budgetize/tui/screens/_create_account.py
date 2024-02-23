"""Module that defines the CreateAccount screen."""

import gettext

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Select

from budgetize.consts import CURRENCIES, TRANSLATIONS_PATH
from budgetize.db import Database
from budgetize.db.orm import Account, AccountType

t = gettext.translation("budgetize", localedir=TRANSLATIONS_PATH, languages=["es"])
_ = t.gettext


class CreateAccount(Screen):
    """Screen that allows the user to create a new account."""

    CSS_PATH = "css/create_account.tcss"

    DB: Database = None  # type: ignore
    BINDINGS = [
        Binding(
            key="c,C", key_display="C", action="pop_screen", description=_("Cancel")
        ),
    ]

    def __init__(self) -> None:
        """Creates a new CreateAccount Screen"""
        CreateAccount.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        """Called when the screen is composed."""

        self.app.sub_title = _("Create Account")
        yield Header()
        yield Footer()

        yield VerticalScroll(
            Grid(
                # Place them in this way because grids are filled in row-order
                Label(_("Account Currency"), id="currency-label"),
                Label(_("Account Name"), id="name-label"),
                Select(
                    self.get_currency_choices(), id="currency-select", allow_blank=False
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
                    )
                ],
            ),
            Label(_("Account Type"), id="account-type-label"),
            Select(
                # TODO: Localize this
                self.get_account_type_choices(),
                id="account-type-select",
                allow_blank=False,
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
            balance: float = self.get_widget_by_id("balance-input").value  # type: ignore
            account_type_name: str = self.get_widget_by_id("account-type-select").value  # type: ignore #pylint: disable=line-too-long

            new_account = Account(
                account_type_name=account_type_name.upper(),
                name=name,
                currency=currency,
                balance=balance,
            )

            self.DB.add_account(new_account)
            self.app.pop_screen()
            self.notify(_("Account created successfully."), title="Account Created")

        elif event.button.id == "cancel-button":
            self.get_widget_by_id("account-name-input").value = ""  # type: ignore
            self.get_widget_by_id("balance-input").value = ""  # type: ignore
            self.app.pop_screen()

    def get_currency_choices(self) -> list[tuple[str, str]]:
        """Returns a list of tuples for the currency select widget"""
        res = []
        for curr in CURRENCIES:
            res.append((f"({curr[0]}) {curr[1]}", curr[0]))

        return res

    def get_account_type_choices(self) -> list[tuple[str, str]]:
        """Returns a list of tuples for the account type select widget"""
        res = []
        for acc in AccountType:
            res.append((acc.name.capitalize(), acc.name.capitalize()))

        return res
