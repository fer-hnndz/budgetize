"""Module that defines the main menu screen"""

import asyncio
from typing import Optional

from arrow import Arrow
from babel.numbers import format_currency, parse_decimal
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Rule
from textual.widgets.data_table import CellKey

from budgetize import CurrencyManager, SettingsManager
from budgetize.db.database import Database
from budgetize.exceptions import ExchangeRateFetchError
from budgetize.tui.modals.confirm_quit import ConfirmQuit
from budgetize.tui.modals.error_modal import ErrorModal
from budgetize.tui.modals.transaction_details import TransactionDetails
from budgetize.tui.screens.add_transaction import AddTransaction
from budgetize.tui.screens.manage_accounts import ManageAccounts
from budgetize.tui.screens.settings import Settings
from budgetize.utils import _


class MainMenu(Screen):
    """Screen that displays the main menu"""

    DB: Database = None  # type: ignore
    CSS_PATH = "css/main_menu.tcss"
    BINDINGS = [
        Binding(
            key="q,Q",
            key_display="Q",
            action="request_quit()",
            description=_("Quit Budgetize"),
        ),
        Binding(
            key="n,N",
            key_display="N",
            action="verify_add_transaction()",
            description=_("Add Transaction"),
        ),
        Binding(
            key="i,I",
            key_display="I",
            action="show_settings()",
            description=_("Open Settings"),
        ),
        Binding(
            key="r, R",
            key_display="R",
            action="refresh_currencies()",
            description=_("Force Exchange Rate Update"),
        ),
    ]

    def __init__(self) -> None:
        """Creates a new MainMenu Screen"""
        super().__init__()
        MainMenu.DB = Database(self.app)
        self.rates_fetched = False

        self.last_account_key: Optional[CellKey] = None
        self.last_account_value: str = "None"
        self.last_recent_transactions_key: Optional[CellKey] = None
        self.last_recent_transactions_value: str = "None"

    def compose(self) -> ComposeResult:
        """Called when screen is composed"""
        self.app.sub_title = _("Main Menu")
        yield Header()
        yield Footer()
        yield Label("Accounts", id="accounts-label")
        yield Rule(orientation="horizontal", line_style="heavy")
        yield Horizontal(
            DataTable(id="accounts-table"),
            # TODO: Convert all other currencies to main currency
            Vertical(
                Label(
                    "...",
                    id="monthly-income",
                ),
                Label(
                    "...",
                    id="monthly-balance",
                ),
                Label(
                    "...",
                    id="monthly-expense",
                ),
            ),
        )
        yield Horizontal(
            Button(_("Create Account"), id="create-account-button"),
            Button(_("Manage Accounts"), id="manage-accounts-button"),
        )
        yield Label(_("Recent Transactions"), id="recent-transactions-label")

        # Generate last 5 transactions
        # TODO: Replace the place holders
        yield DataTable(id="recent-transactions-table")

        yield Rule(orientation="horizontal")

    async def on_mount(self) -> None:
        """Called when the screen is about to be shown"""
        self.last_account_key = None
        self.last_account_value = ""
        self.last_recent_transactions_key = None
        self.last_recent_transactions_value = ""

        self.run_worker(self.update_ui_info, exclusive=True)  # type: ignore

    async def update_ui_info(self) -> None:
        """Lets the user now that the app is about to update exchange rates and update UI elements"""
        # TODO: Show error log when the exchange couldnt be fetched.

        monthly_income_label: Label = self.get_widget_by_id(
            "monthly-income"
        )  # type:ignore
        monthly_balance_label: Label = self.get_widget_by_id(
            "monthly-balance"
        )  # type:ignore
        monthly_expense_label: Label = self.get_widget_by_id(
            "monthly-expense"
        )  # type:ignore

        try:
            currency_manager = CurrencyManager(SettingsManager().get_base_currency())

            rates_update_task = asyncio.create_task(
                currency_manager.update_invalid_rates()
            )

            if not self.rates_fetched:
                monthly_income_label.update("...")
                monthly_balance_label.update("...")
                monthly_expense_label.update("...")

            # If rates have been fetched (or attempted), just update UI
            if self.rates_fetched or not currency_manager.has_expired_rates():
                self._update_account_tables()
                self._update_recent_transactions_table()
                await self._update_balance_labels()
                return

            self.app.notify(
                title=_("Updating Currency Rates"),
                message=_(
                    "Please wait while we retrieve the latest currency conversion rates for you."
                ),
                severity="warning",
                timeout=6,
            )

            self._update_account_tables()
            self._update_recent_transactions_table()

            await rates_update_task
        except ExchangeRateFetchError as e:
            msg = str(e) + _("\n\n Using outdated exchange rates for now.")
            self.app.push_screen(
                ErrorModal(title=_("Error Fetching Exchange Rates"), traceback_msg=msg)
            )
        finally:
            await self._update_balance_labels()
            if not self.rates_fetched:
                self.app.notify(
                    title=_("Updating Currency Rates"),
                    message=_("Updated all currency rates."),
                    severity="information",
                    timeout=6,
                )
            self.rates_fetched = True

    def on_screen_resume(self) -> None:
        """Called when the screen is now the current screen"""
        self.app.sub_title = _("Main Menu")
        self.run_worker(self.update_ui_info, exclusive=True)  # type: ignore

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handler"""

        if event.button.id == "create-account-button":
            self.app.push_screen("create_account")
        if event.button.id == "manage-accounts-button":
            accounts = self.DB.get_accounts()
            if sum(1 for _ in accounts) > 0:  # Get the length of the generator
                self.app.push_screen(ManageAccounts())
            else:
                self.app.notify(
                    severity="warning",
                    title=_("Cannot Manage Accounts"),
                    message=_("You must need atleast one account to manage accounts."),
                )

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Called when a cell in the DataTable is selected"""

        if event.data_table.id == "recent-transactions-table":
            row_pos = event.coordinate.row
            for n, row_key in enumerate(event.data_table.rows):
                if (n == row_pos) and (row_key.value is not None):
                    details_screen = TransactionDetails(int(row_key.value))
                    self.app.push_screen(details_screen)

    async def force_reload(self) -> None:
        """Force reloads all exchange rates"""

    def _update_recent_transactions_table(self) -> None:
        """Updates the recent transactions DataTable widget."""

        table: DataTable = self.get_widget_by_id("recent-transactions-table")  # type: ignore
        recent_transactions = self.DB.get_all_recent_transactions()
        table.clear(columns=True)
        table.add_columns(
            _("Account"), _("Amount"), _("Date"), _("Category"), _("Description")
        )

        for trans in recent_transactions:
            # Should never happen.
            if trans.account_id == None:
                continue

            if trans.account_id is None:
                continue

            account = self.DB.get_account_by_id(int(trans.account_id))
            color = "[green]" if trans.amount > 0 else "[red]"
            date = Arrow.fromtimestamp(trans.timestamp).format("MM/DD/YYYY")

            table.add_row(
                account.name,
                f"{color}{format_currency(trans.amount, account.currency, locale = SettingsManager().get_locale())}",
                date,
                trans.category,
                trans.description,
                key=str(trans.id),
            )

    def _update_account_tables(self) -> None:
        """Updates the accounts DataTable widget"""

        table: DataTable = self.get_widget_by_id("accounts-table")  # type: ignore
        table.clear(columns=True)
        table.add_columns(
            _("Account Name"),
            _("Balance"),
        )

        for acc in self.DB.get_accounts():
            table.add_row(
                acc.name,
                format_currency(
                    self.DB.get_account_balance(acc.id),
                    acc.currency,
                    locale=SettingsManager().get_locale(),
                ),
            )

    async def _update_balance_labels(self) -> None:
        """(Coroutine) Updates monthly income/balance/expense labels"""

        monthly_income_label: Label = self.get_widget_by_id(
            "monthly-income"
        )  # type:ignore
        monthly_balance_label: Label = self.get_widget_by_id(
            "monthly-balance"
        )  # type:ignore
        monthly_expense_label: Label = self.get_widget_by_id(
            "monthly-expense"
        )  # type:ignore

        try:

            monthly_income: float = await self.DB.get_monthly_income()
            monthly_expense: float = await self.DB.get_monthly_expense()
            balance: float = round(monthly_income + monthly_expense, 2)
            main_currency = SettingsManager().get_base_currency()

            income_color = "[green]" if monthly_income > 0 else "[red]"
            expense_color = "[green]" if monthly_expense > 0 else "[red]"
            balance_color = "[green]" if balance >= 0 else "[red]"

            user_locale = SettingsManager().get_locale()

            monthly_income_label.update(
                _("Income this Month\n{income_color}{monthly_income}").format(
                    income_color=income_color,
                    monthly_income=format_currency(
                        monthly_income,
                        main_currency,
                        locale=user_locale,
                    ),
                )
            )

            monthly_balance_label.update(
                _("Balance\n{balance_color}{balance}").format(
                    balance_color=balance_color,
                    balance=format_currency(
                        balance,
                        main_currency,
                        locale=user_locale,
                    ),
                )
            )
            monthly_expense_label.update(
                _("Expenses this Month\n{expense_color}{monthly_expense}").format(
                    expense_color=expense_color,
                    monthly_expense=format_currency(
                        monthly_expense,
                        main_currency,
                        locale=user_locale,
                    ),
                )
            )

        except ExchangeRateFetchError as e:
            msg = str(e) + _(
                "\n\nConnect to the internet to be able to use Budgetize.\nOr create an issue at Github to get support."
            )
            modal = ErrorModal(
                title=_("Error Fetching Exchange Rates"), traceback_msg=msg
            )
            self.app.push_screen(modal)
            self.rates_fetched = True

            monthly_income_label.update("...")
            monthly_balance_label.update("...")
            monthly_expense_label.update("...")

    # ==================== App Bindings ====================

    def action_verify_add_transaction(self) -> None:
        """
        Verifies if there is atleast one account to add a transaction to.
        If there is, it pushes the add_transaction screen.
        If there isn't, it notifies the user.
        """

        accounts = 0
        for acc in self.DB.get_accounts():
            accounts += 1
        if accounts:
            self.app.push_screen(AddTransaction())
        else:
            print("Showing toast")
            self.app.notify(
                severity="warning",
                title=_("Cannot add a Transaction"),
                message=_("You must need atleast one account to add a transaction."),
            )

    def action_request_quit(self) -> None:
        """Shows the modal to quit the app"""
        self.app.push_screen(ConfirmQuit())

    def action_show_settings(self) -> None:
        """Opens the settings."""
        self.rates_fetched = False
        self.app.push_screen(Settings())

    async def on_data_table_cell_highlighted(
        self, event: DataTable.CellHighlighted
    ) -> None:
        """Called when a cell in the DataTable is highlighted"""

        if event.control.id == "accounts-table":
            accounts_table: DataTable = self.get_widget_by_id(
                "accounts-table"
            )  # type:ignore

            # User clicked in balance column
            if event.coordinate.column == 1:
                if self.last_account_key is None:
                    self.last_account_key = event.cell_key
                    self.last_account_value = str(event.value)

                else:
                    accounts_table.update_cell(
                        self.last_account_key.row_key,
                        self.last_account_key.column_key,
                        self.last_account_value,
                    )

                    self.last_account_key = event.cell_key
                    self.last_account_value = str(event.value)

                # 0.00\xa0USD - format
                numbers: str = event.value.split("\xa0")[0]  # type:ignore
                decimal_value = parse_decimal(
                    numbers,
                    locale=SettingsManager().get_locale(),
                )

                account_name = accounts_table.get_cell_at(event.coordinate.left())
                account = self.DB.get_account_by_name(account_name)

                # Do not show exchange rate of the currency since its the same
                if account.currency == SettingsManager().get_base_currency():
                    return

                main_currency = SettingsManager().get_base_currency()
                exchange_rate = await CurrencyManager(main_currency).get_exchange(
                    account.currency
                )

                amt = float(str(decimal_value))
                formatted_currency = format_currency(
                    number=(amt / exchange_rate),
                    currency=main_currency,
                    locale=SettingsManager().get_locale(),
                ).replace("\xa0", " ")

                print(formatted_currency)
                accounts_table.update_cell(
                    event.cell_key.row_key,
                    event.cell_key.column_key,
                    str(formatted_currency),
                    update_width=True,
                )

                print("Updated exchange rate")
            # User selected other column instead of balance
            elif self.last_account_key is not None:
                accounts_table.update_cell(
                    self.last_account_key.row_key,
                    self.last_account_key.column_key,
                    self.last_account_value,
                )

                self.last_account_key = None
                self.last_account_value = ""

        if event.control.id == "recent-transactions-table":
            pass
