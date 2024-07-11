"""Module that defines the main menu screen"""

import logging
from random import choice, randint
from typing import Optional

from arrow import Arrow
from babel.numbers import format_currency, parse_decimal
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    ProgressBar,
    TabbedContent,
    TabPane,
)
from textual.widgets.data_table import CellKey

from budgetize import CurrencyManager, SettingsManager
from budgetize.consts import RICH_COLORS
from budgetize.db.database import Database
from budgetize.exceptions import ExchangeRateFetchError
from budgetize.tui.modals.confirm_quit import ConfirmQuit
from budgetize.tui.modals.error_modal import ErrorModal
from budgetize.tui.modals.transaction_details import TransactionDetails
from budgetize.tui.screens.add_transaction import AddTransaction
from budgetize.tui.screens.manage_accounts import ManageAccounts
from budgetize.tui.screens.settings import Settings
from budgetize.tui.screens.transfer import TransferScreen
from budgetize.utils import _

logger = logging.getLogger(__name__)


class MainMenu(Screen):
    """Screen that displays the main menu"""

    TOTAL_SPENT = 0
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
            key="r,R",
            key_display="R",
            action="refresh_currencies()",
            description=_("Force Exchange Rate Update"),
        ),
        Binding(
            key="s,S",
            key_display="S",
            action="show_settings()",
            description=_("Open Settings"),
        ),
    ]

    def __init__(self) -> None:
        """Creates a new MainMenu Screen"""
        super().__init__()
        MainMenu.DB = Database(self.app)
        self.rates_fetched = False

        # Keys for storing actual values to show main currency
        self.last_account_key: Optional[CellKey] = None
        self.last_account_value: str = "None"
        self.last_recent_transactions_key: Optional[CellKey] = None
        self.last_recent_transactions_value: str = "None"

    def compose(self) -> ComposeResult:
        """Called when screen is composed"""
        logger.info("Composing MainMenu...")

        self.app.sub_title = _("Main Menu")
        yield Header()
        yield Footer()
        with TabbedContent(id="tabs"):
            with TabPane(_("Accounts"), id="accounts-tab"):
                with Horizontal():
                    yield DataTable(id="accounts-table")
                    # Monthly balances
                    yield Vertical(
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
                        id="balance-labels",
                    )
                with Horizontal():
                    yield Button(
                        _("Create Account"),
                        id="create-account-button",
                        variant="success",
                    )
                    yield Button(
                        _("Manage Accounts"),
                        id="manage-accounts-button",
                        variant="primary",
                    )
                with Horizontal():
                    yield Button(
                        _("New Transanction"),
                        id="transaction-button",
                        variant="success",
                    )
                    yield Button(
                        _("Transfer between Accounts"),
                        id="transfer-btn",
                        variant="primary",
                    )

            with TabPane(_("Recent Transactions"), id="transactions-tab"):
                yield Label(
                    _(
                        "[bold][sandy_brown]Tip:[/bold][/sandy_brown] [italic]Click on a transaction to manage it."
                    ),
                    id="transaction-tip",
                )
                yield DataTable(id="recent-transactions-table")

            with TabPane(_("Budgets"), id="budgets-tab"):

                with Center():
                    yield Label(
                        "[bold][lime]Monthly Goal:[/lime][/bold] $1000", id="goal-label"
                    )

                    with Horizontal(id="budget-categories"):
                        # Loop through Budget categories
                        spend_limit = [250, 700, 50]
                        i = 0
                        for category in ["Food", "Entertainment", "Transportation"]:
                            color = choice(RICH_COLORS)
                            spent = randint(10, round(spend_limit[i] * 1.15))
                            MainMenu.TOTAL_SPENT += spent
                            balance_color = (
                                "[green]" if spent < spend_limit[i] else "[red]"
                            )

                            yield Label(
                                f"[{color}]{category}[/{color}]\nLimit: [{color}]{spend_limit[i]}[/{color}]\nCurrent Spent:{balance_color}{spent}",
                            )
                            i += 1

                    with Center():
                        yield Label("Budget Progress")
                        yield ProgressBar(
                            total=1000, show_eta=False, id="budget-progress"
                        )

    async def on_mount(self) -> None:
        """Called when the screen is about to be shown"""
        logger.info("Mounting MainMenu...")
        self.last_account_key = None
        self.last_account_value = ""
        self.last_recent_transactions_key = None
        self.last_recent_transactions_value = ""

        logger.info("Runnning background worker for updating UI...")

    def after_layout(self) -> None:
        self.run_worker(self.update_ui_info, exclusive=True)  # type: ignore

    async def update_ui_info(self) -> None:
        """Lets the user now that the app is about to update exchange rates and update UI elements"""
        labels_container = self.query_one("#balance-labels", expect_type=Vertical)
        logger.debug(labels_container.children)
        labels_container.loading = True
        try:
            base_currency = SettingsManager().get_base_currency()
            currency_manager = CurrencyManager(base_currency)
            logger.info(
                f"Created a new CurrencyManager instance with base currency {base_currency}",
            )

            if currency_manager.has_expired_rates() and not self.rates_fetched:
                logger.info("Attempting to update expired rates...")
                self.app.notify(
                    title=_("Updating Currency Rates"),
                    message=_(
                        "Please wait while we retrieve the latest currency conversion rates for you."
                    ),
                    severity="warning",
                    timeout=6,
                )
                await currency_manager.update_invalid_rates()

            # Once the rates have been fetched (successfully or not), update UI without checking for outdated rates
            logger.info(
                "Rates have been fetched or attempted. Updating UI without checking for outdated rates.",
            )

            self._update_account_tables()
            self._update_recent_transactions_table()
            await self._update_balance_labels()

            progress = self.query_one("#budget-progress", expect_type=ProgressBar)
            progress.advance(MainMenu.TOTAL_SPENT)

        except ExchangeRateFetchError as e:
            msg = f"{e}\n\n Using outdated exchange rates for now."
            self.app.push_screen(
                ErrorModal(title=_("Error Fetching Exchange Rates"), traceback_msg=msg),
            )

        labels_container.loading = False
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
        # Reset key values to avoid crashes
        self.last_account_key = None
        self.last_account_value = "None"
        self.last_recent_transactions_key = None
        self.last_recent_transactions_value = "None"

        self.app.sub_title = _("Main Menu")
        self.run_worker(self.update_ui_info, exclusive=True)  # type: ignore

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handler"""
        if event.button.id == "create-account-button":
            self.app.push_screen("create_account")
            # Set rates as not fetched in case user creates an account with a new currency
            self.rates_fetched = False
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
        if event.button.id == "transfer-btn":
            self.action_create_transfer()
            return

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Called when a cell in the DataTable is selected"""
        if event.data_table.id == "recent-transactions-table":
            row_pos = event.coordinate.row
            for n, row_key in enumerate(event.data_table.rows):
                if (n == row_pos) and (row_key.value is not None):
                    details_screen = TransactionDetails(int(row_key.value))
                    self.app.push_screen(details_screen)

    def _update_recent_transactions_table(self) -> None:
        """Updates the recent transactions DataTable widget."""
        logger.info("Updating recent transactions table...")
        table: DataTable = self.get_widget_by_id("recent-transactions-table")  # type: ignore
        recent_transactions = self.DB.get_all_recent_transactions()
        table.clear(columns=True)
        logger.info("Cleared columns from recent transactions table.")
        table.add_columns(
            _("Account"),
            _("Amount"),
            _("Date"),
            _("Category"),
            _("Description"),
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
                f"{color}{format_currency(trans.amount, account.currency, locale=SettingsManager().get_locale())}",
                date,
                trans.category,
                trans.description,
                key=str(trans.id),
            )

    def _update_account_tables(self) -> None:
        """Updates the accounts DataTable widget"""
        logger.info("Updating account tables...")
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
            "monthly-income", expect_type=Label
        )
        monthly_balance_label: Label = self.get_widget_by_id(
            "monthly-balance", expect_type=Label
        )
        monthly_expense_label: Label = self.get_widget_by_id(
            "monthly-expense", expect_type=Label
        )

        try:
            monthly_income: float = await self.DB.get_monthly_income()
            monthly_expense: float = await self.DB.get_monthly_expense()
            balance: float = round(monthly_income + monthly_expense, 2)
            base_currency = SettingsManager().get_base_currency()

            logger.info(
                f"Monthly Income: {monthly_income} | Monthly Expense: {monthly_expense} | Balance: {balance}",
            )

            income_color = "[green]" if monthly_income > 0 else "[red]"
            expense_color = "[green]" if monthly_expense > 0 else "[red]"
            balance_color = "[green]" if balance >= 0 else "[red]"

            user_locale = SettingsManager().get_locale()

            monthly_income_label.update(
                _("Income this Month\n{income_color}{monthly_income}").format(
                    income_color=income_color,
                    monthly_income=format_currency(
                        monthly_income,
                        base_currency,
                        locale=user_locale,
                    ),
                ),
            )

            monthly_balance_label.update(
                _("Balance\n{balance_color}{balance}").format(
                    balance_color=balance_color,
                    balance=format_currency(
                        balance,
                        base_currency,
                        locale=user_locale,
                    ),
                ),
            )
            monthly_expense_label.update(
                _("Expenses this Month\n{expense_color}{monthly_expense}").format(
                    expense_color=expense_color,
                    monthly_expense=format_currency(
                        monthly_expense,
                        base_currency,
                        locale=user_locale,
                    ),
                ),
            )

        except ExchangeRateFetchError as e:
            logger.error(f"Error fetching exchange rates: {e}")
            msg = str(e) + _(
                "\n\nConnect to the internet to be able to use Budgetize.\nOr create an issue at Github to get support.",
            )
            logger.info("Showing error modal...")
            modal = ErrorModal(
                title=_("Error Fetching Exchange Rates"),
                traceback_msg=msg,
            )
            self.app.push_screen(modal)

    # ==================== App Bindings ====================

    def action_verify_add_transaction(self) -> None:
        """Verifies if there is atleast one account to add a transaction to.
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
        logger.info("Pushing ConfirmQuit Modal...")
        self.app.push_screen(ConfirmQuit())

    def action_show_settings(self) -> None:
        """Opens the settings."""
        logger.info("Pushing Settings Screen...")
        self.rates_fetched = False
        self.app.push_screen(Settings())

    async def on_data_table_cell_highlighted(
        self,
        event: DataTable.CellHighlighted,
    ) -> None:
        """Called when a cell in the DataTable is highlighted"""
        if event.control.id == "accounts-table":
            accounts_table: DataTable = self.get_widget_by_id(
                "accounts-table",
            )  # type:ignore

            # User clicked in balance column
            if event.coordinate.column == 1:
                if self.last_account_key is None:
                    logger.info(
                        "There was not previous selected balance cell. Updating...",
                    )
                    self.last_account_key = event.cell_key
                    self.last_account_value = str(event.value)

                else:
                    logger.info(
                        "Resetting last selected cell value and updating to new value...",
                    )
                    accounts_table.update_cell(
                        self.last_account_key.row_key,
                        self.last_account_key.column_key,
                        self.last_account_value,
                    )

                    self.last_account_key = event.cell_key
                    self.last_account_value = str(event.value)

                # 0.00\xa0USD - format
                logger.info(f"Parsing currency from cell: {event.value}")
                detected_decimal = ""
                for char in str(event.value):
                    if char.strip().isdigit() or char.strip() in [",", "."]:
                        detected_decimal += char

                logger.debug(f"Detected decimals: {detected_decimal}")

                decimal_value = parse_decimal(
                    detected_decimal,
                    locale=SettingsManager().get_locale(),
                )
                logger.debug(f"Decimal value: {decimal_value}")
                account_name = accounts_table.get_cell_at(event.coordinate.left())
                account = self.DB.get_account_by_name(account_name)

                # Do not show exchange rate of the currency since its the same
                if account.currency == SettingsManager().get_base_currency():
                    logger.info("Currency is the same as base currency. Not updating.")
                    return

                main_currency = SettingsManager().get_base_currency()
                exchange_rate = await CurrencyManager(main_currency).get_exchange(
                    account.currency,
                )
                logger.info(f"Exchange rate got: {exchange_rate}")

                amt = float(str(decimal_value))
                formatted_currency = format_currency(
                    number=(amt / exchange_rate),
                    currency=main_currency,
                    locale=SettingsManager().get_locale(),
                ).replace("\xa0", " ")

                accounts_table.update_cell(
                    event.cell_key.row_key,
                    event.cell_key.column_key,
                    str(formatted_currency),
                    update_width=True,
                )

                logger.info(f"Updated exchange rate to: {formatted_currency}")

            # User selected other column instead of balance
            elif self.last_account_key is not None:
                logger.info("Resetting last selected cell value...")
                accounts_table.update_cell(
                    self.last_account_key.row_key,
                    self.last_account_key.column_key,
                    self.last_account_value,
                )

                self.last_account_key = None
                self.last_account_value = ""

    def action_refresh_currencies(self) -> None:
        """Called when user hits the binding to refresh currencies"""
        self.notify(
            title="Unable to Update",
            message="Missing implementation",
            severity="error",
        )

    def action_create_transfer(self) -> None:
        """Called when user hits binding to make a transfer"""
        logger.info("Pushing TransferScreen...")
        self.app.push_screen(TransferScreen())
