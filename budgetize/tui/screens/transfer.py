"""Module that defines the transfer screen between accounts"""

from arrow import Arrow
from babel.numbers import format_currency
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.validation import Number
from textual.widgets import Button, Footer, Header, Input, Label, Select

from budgetize import CurrencyManager, SettingsManager
from budgetize.db.database import Database
from budgetize.utils import _


class TransferScreen(Screen):
    """Screen used to transfer funds between user accounts"""

    DB: Database = Database()
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
            # Use ... because an account has not been selected yet
            yield Label(
                "[bold cyan]Select an Origin Account",
                id="origin-balance",
            )
            yield Label(
                "[bold cyan]Select a Destination Account",
                id="destination-balance",
            )

        with Horizontal():
            with Vertical():
                yield Label(_("Origin Account"), id="origin-label")
                yield Select(
                    self.get_accounts_for_select(),
                    id="origin-select",
                    allow_blank=False,
                )
                yield Label(_("Amount to Tranfer"), id="transfer-label")
                yield Input(
                    placeholder="100.00",
                    type="number",
                    validators=Number(minimum=1),
                    id="transfer-input",
                )

            with Vertical():
                yield Label(_("Destination Account"), id="destination-label")
                yield Select(
                    self.get_accounts_for_select(),
                    id="destination-select",
                    allow_blank=False,
                )

        with Horizontal(id="btn-container"):
            yield Button.success(_("Confirm Transfer"), id="transfer-btn")
            yield Button.error(_("Cancel"), id="cancel-btn")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button handler"""

        if event.button.id == "transfer-btn":
            origin_select: Select = self.get_widget_by_id(
                "origin-select"
            )  # type:ignore
            origin_account = TransferScreen.DB.get_account_by_id(
                int(str(origin_select.value))
            )

            destination_select: Select = self.get_widget_by_id(
                "destination-select"
            )  # type:ignore
            destination_account = TransferScreen.DB.get_account_by_id(
                int(str(destination_select.value))
            )

            if origin_account.id == destination_account.id:
                self.app.notify(
                    title=_("Error Transfering Funds"),
                    message=_("Origin and Destination Accounts can not be the same."),
                    severity="error",
                )
                return

            transfer_funds = self.get_transfer_funds()

            if transfer_funds == 0:
                self.app.notify(
                    title=_("Error Transfering Funds"),
                    message=_("Transfer amount has to be atleast 1."),
                    severity="error",
                )
                return

            origin_balance = TransferScreen.DB.get_account_balance(origin_account.id)
            destination_balance = TransferScreen.DB.get_account_balance(
                destination_account.id
            )

            if transfer_funds > origin_balance:
                self.app.notify(
                    title=_("Error Transfering Funds"),
                    message=_("Insufficient funds in Origin account."),
                    severity="error",
                )
                return

            exchange_rate = 1.0
            if destination_account.currency != origin_account.currency:
                exchange_rate = await CurrencyManager(
                    origin_account.currency
                ).get_exchange(destination_account.currency)

            TransferScreen.DB.add_transaction(
                account_id=origin_account.id,
                amount=-1 * transfer_funds,
                description="-",
                category="",
                timestamp=Arrow.now().timestamp(),
                visible=False,
            )

            TransferScreen.DB.add_transaction(
                account_id=destination_account.id,
                amount=transfer_funds * exchange_rate,
                description="-",
                category="",
                timestamp=Arrow.now().timestamp(),
                visible=False,
            )

            self.app.notify(
                title=_("Funds Transfered"),
                message=_("Funds have been successfully transfered."),
                severity="information",
            )
            self.app.pop_screen()
        if event.button.id == "cancel-btn":
            self.app.pop_screen()

    def get_transfer_funds(self) -> float:
        """Returns the transfer funds the user entered"""
        amount_input: Input = self.get_widget_by_id("transfer-input")  # type:ignore
        funds_to_transfer = 0.0

        try:
            funds_to_transfer = float(amount_input.value)

            if funds_to_transfer < 0:
                funds_to_transfer = 0

            return funds_to_transfer
        except ValueError:
            return 0

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Input handler"""
        await self.update_transfer_info()

    async def on_select_changed(self, event: Select.Changed) -> None:
        """Select handler"""
        await self.update_transfer_info()

    async def update_transfer_info(self) -> None:
        """Function that updates labels and balance data temporarily"""
        origin_select: Select = self.get_widget_by_id("origin-select")  # type:ignore

        origin_account = TransferScreen.DB.get_account_by_id(
            int(str(origin_select.value))
        )
        origin_label: Label = self.get_widget_by_id("origin-balance")  # type:ignore

        funds_to_transfer = self.get_transfer_funds()
        origin_balance = TransferScreen.DB.get_account_balance(origin_account.id)

        if funds_to_transfer > origin_balance:
            origin_label.update(
                _(
                    "Origin Account ({account_name}) New Balance\n[bold red]Insufficient funds."
                ).format(account_name=origin_account.name)
            )
            return

        origin_formatted_balance = format_currency(
            number=origin_balance - funds_to_transfer,
            currency=origin_account.currency,
            locale=SettingsManager().get_locale(),
        )

        origin_label.update(
            _(
                "Origin Account ({account_name}) New Balance\n{color}{formatted_new_balance}"
            ).format(
                account_name=origin_account.name,
                color="[red]" if funds_to_transfer > 0 else "[cyan]",
                formatted_new_balance=origin_formatted_balance,
            )
        )

        destination_select: Select = self.get_widget_by_id(
            "destination-select"
        )  # type:ignore

        destination_account = TransferScreen.DB.get_account_by_id(
            int(str(destination_select.value))
        )
        destination_label: Label = self.get_widget_by_id("destination-balance")  # type: ignore

        if destination_account.id == origin_account.id:
            destination_label.update(
                _(
                    "Destination Account New Balance\n[bold red]Please select a different account."
                )
            )
            return

        exchange_rate = 1.0
        if destination_account.currency != origin_account.currency:
            exchange_rate = await CurrencyManager(origin_account.currency).get_exchange(
                destination_account.currency
            )

        destination_balance = TransferScreen.DB.get_account_balance(
            destination_account.id
        )
        destination_formatted_balance = format_currency(
            number=destination_balance + (funds_to_transfer * exchange_rate),
            currency=destination_account.currency,
            locale=SettingsManager().get_locale(),
        )

        destination_label.update(
            _(
                "Destination Account ({account_name}) New Balance\n{color}{formatted_new_balance}"
            ).format(
                account_name=destination_account.name,
                color="[green]" if funds_to_transfer > 0 else "[cyan]",
                formatted_new_balance=destination_formatted_balance,
            )
        )

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
