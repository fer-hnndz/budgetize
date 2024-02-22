"""Module that defines the main menu screen"""

import gettext

from arrow import Arrow
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Rule

from budgetize.db import Database
from budgetize.tui.modals import ConfirmQuit, TransactionDetails
from budgetize.tui.screens import AddTransaction

# Import directly from the class file to avoid circular imports
from budgetize.tui.screens._manage_accounts import ManageAccounts

t = gettext.translation(
    "budgetize", localedir="./budgetize/translations", languages=["es"]
)
_ = t.gettext


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
    ]

    def __init__(self) -> None:
        """Creates a new MainMenu Screen"""
        MainMenu.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        """Called when screen is composed"""

        monthly_income = self.DB.get_monthly_income()
        monthly_expense = self.DB.get_monthly_expense()
        balance = monthly_income + monthly_expense

        income_color = "[green]" if monthly_income > 0 else "[red]"
        expense_color = "[green]" if monthly_expense > 0 else "[red]"
        balance_color = "[green]" if balance >= 0 else "[red]"

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
                    _("Income this Month\n{income_color}{monthly_income}").format(
                        income_color=income_color, monthly_income=monthly_income
                    ),
                    id="monthly-income",
                ),
                Label(
                    _("Balance\n{balance_color}{balance}").format(
                        balance_color=balance_color, balance=balance
                    ),
                    id="monthly-balance",
                ),
                Label(
                    _("Expenses this Month\n{expense_color}{monthly_expense}").format(
                        expense_color=expense_color, monthly_expense=monthly_expense
                    ),
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

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Called when a cell in the DataTable is selected"""

        if event.data_table.id == "recent-transactions-table":
            row_pos = event.coordinate.row
            for n, row_key in enumerate(event.data_table.rows):
                if (n == row_pos) and (row_key.value is not None):
                    details_screen = TransactionDetails(int(row_key.value))
                    self.app.push_screen(details_screen)
                    # details_screen.set_transaction(row_key.value)

    def on_mount(self) -> None:
        """Called when the screen widgets are mounted"""

        self._update_account_tables()
        self._update_recent_transactions_table()

    def _update_recent_transactions_table(self) -> None:
        """Updates the recent transactions DataTable widget"""

        recent_transactions = self.DB.get_all_recent_transactions()
        table: DataTable = self.get_widget_by_id("recent-transactions-table")  # type: ignore
        table.clear(columns=True)
        table.add_columns(
            _("Account"), _("Amount"), _("Date"), _("Category"), _("Description")
        )

        for trans in recent_transactions:
            account = self.DB.get_account_by_id(trans.account_id)
            color = "[green]" if trans.amount > 0 else "[red]"
            date = Arrow.fromtimestamp(trans.timestamp).format("MM/DD/YYYY")

            table.add_row(
                account.name,
                f"{color}{account.currency} {str(trans.amount)}",
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
            _("Account Name"), _("Account Type"), _("Balance"), _("Currency")
        )

        for acc in self.DB.get_accounts():
            table.add_row(
                acc.name, acc.account_type.name.capitalize(), acc.balance, acc.currency
            )

    def _update_balance_labels(self) -> None:
        """Updates monthly income/balance/expense labels"""
        monthly_income = self.DB.get_monthly_income()
        monthly_expense = self.DB.get_monthly_expense()
        balance = monthly_income + monthly_expense

        income_color = "[green]" if monthly_income > 0 else "[red]"
        expense_color = "[green]" if monthly_expense > 0 else "[red]"
        balance_color = "[green]" if balance >= 0 else "[red]"

        monthly_income_label: Label = self.get_widget_by_id(
            "monthly-income"
        )  # type:ignore
        monthly_balance_label: Label = self.get_widget_by_id(
            "monthly-balance"
        )  # type:ignore
        monthly_expense_label: Label = self.get_widget_by_id(
            "monthly-expense"
        )  # type:ignore

        monthly_income_label.update(
            _("Income this Month\n{income_color}{monthly_income}").format(
                income_color=income_color, monthly_income=monthly_income
            )
        )
        monthly_balance_label.update(
            _("Balance\n{balance_color}{balance}").format(
                balance_color=balance_color, balance=balance
            )
        )
        monthly_expense_label.update(
            _("Expenses this Month\n{expense_color}{monthly_expense}").format(
                expense_color=expense_color, monthly_expense=monthly_expense
            )
        )

    def on_screen_resume(self) -> None:
        """Called when the screen is now the current screen"""
        self._update_account_tables()
        self._update_recent_transactions_table()
        self._update_balance_labels()

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

    # ==================== App Bindings ====================

    def action_verify_add_transaction(self) -> None:
        """
        Verifies if there is atleast one account to add a transaction to.
        If there is, it pushes the add_transaction screen.
        If there isn't, it notifies the user.
        """

        accounts = 0
        for _ in self.DB.get_accounts():
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
