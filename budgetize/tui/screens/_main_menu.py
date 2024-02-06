"""Module that defines the main menu screen"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Rule

from budgetize.db import Database
from budgetize.tui.modals import ConfirmQuit

# Import directly from the class file to avoid circular imports
from budgetize.tui.screens._manage_accounts import ManageAccounts


class MainMenu(Screen):
    """Screen that displays the main menu"""

    DB: Database = None  # type: ignore
    CSS_PATH = "css/main_menu.tcss"
    BINDINGS = [
        Binding(
            key="q,Q",
            key_display="Q",
            action="request_quit()",
            description="Quit Budgetize",
        ),
        Binding(
            key="n,N",
            key_display="N",
            action="verify_add_transaction()",
            description="Add Transaction",
        ),
    ]

    def __init__(self) -> None:
        """Creates a new MainMenu Screen"""
        MainMenu.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        """Called when screen is composed"""

        self.app.sub_title = "Main Menu"
        yield Header()
        yield Footer()
        yield Label("Accounts", id="accounts-label")
        yield Rule(orientation="horizontal", line_style="heavy")
        yield Horizontal(
            DataTable(id="accounts-table"),
            Vertical(
                Label("Income this Month\n[green]L. 250.00[/green]"),
                Label("Balance\n[green]L. 250.00[/green]"),
                Label("Expenses this Month\n[red]L. 250.00[/red]"),
            ),
        )
        yield Horizontal(
            Button("Create Account", id="create-account-button"),
            Button("Manage Accounts", id="manage-accounts-button"),
        )
        yield Label("Recent Transactions", id="recent-transactions-label")

        # Generate last 5 transactions
        # TODO: Replace the place holders
        yield DataTable(id="recent-transactions-table")

        yield Rule(orientation="horizontal")

    def on_mount(self) -> None:
        """Called when the screen widgets are mounted"""

        self._update_account_tables()
        self._update_recent_transactions_table()

    def _update_recent_transactions_table(self) -> None:
        """Updates the recent transactions DataTable widget"""

        # TODO: Implement this method based on users' transactions
        table: DataTable = self.get_widget_by_id("recent-transactions-table")  # type: ignore
        table.clear(columns=True)
        table.add_columns("Account", "Amount", "Date", "Category")
        table.add_row("Wallet", "[red] HNL 250.00", "2021-01-01", "Food")
        table.add_row("Wallet", "[green] HNL 250.00", "2021-01-01", "Income")

    def _update_account_tables(self) -> None:
        """Updates the accounts DataTable widget"""

        self.notify(
            "Running in DevMode"
            if "devtools" in self.app.features
            else "Accounts Normal"
        )

        table: DataTable = self.get_widget_by_id("accounts-table")  # type: ignore
        table.clear(columns=True)
        table.add_columns("Account Name", "Account Type", "Balance", "Currency")

        for acc in self.DB.get_accounts():
            table.add_row(
                acc.name, acc.account_type.name.capitalize(), acc.balance, acc.currency
            )

    def on_screen_resume(self) -> None:
        """Called when the screen is now the current screen"""
        print("Main Menu is now current")
        self._update_account_tables()

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
                    title="Cannot Manage Accounts",
                    message="You must need atleast one account to manage accounts.",
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
            self.app.push_screen("add_transaction")
        else:
            print("Showing toast")
            self.app.notify(
                severity="warning",
                title="Cannot add a Transaction",
                message="You must need atleast one account to add a transaction.",
            )

    def action_request_quit(self) -> None:
        """Shows the modal to quit the app"""
        self.app.push_screen(ConfirmQuit())
