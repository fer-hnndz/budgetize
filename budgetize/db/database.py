"""Definition of Database class that handles database operations"""

import logging
import os
from pathlib import Path
from typing import Iterator, Optional

from arrow import Arrow
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from textual.app import App

from budgetize import CurrencyManager, SettingsManager
from budgetize.consts import APP_FOLDER_PATH, BACKUPS_FOLDER, DB_FILE_NAME, PROD_DB_URL
from budgetize.db.orm._base import Base
from budgetize.db.orm.account import Account
from budgetize.db.orm.transactions import Transaction

logger = logging.getLogger(__name__)


class Database:
    """This class is the API for interacting with the database.
    All read and writes are done here which may include utilities for converting currencies, for example.
    """

    engine = create_engine(PROD_DB_URL)
    backup_done = False

    def __init__(self, app: Optional[App] = None):
        """Initializes a Database instance.

        Args:
        ----
            app (App): The application instance.

        """
        self.app = app
        self.settings = SettingsManager()
        self.dev_db = True
        self._init_connection()

    def _init_connection(self) -> None:
        """Initializes the connection to the database."""
        logger.info("Initializing database connection...")
        if self.app is None:
            Database.engine = create_engine("sqlite:///test_db.sqlite")
            self.dev_db = True
        else:
            Database.engine = create_engine(
                (
                    PROD_DB_URL
                    if "devtools" not in self.app.features
                    else "sqlite:///test_db.sqlite"
                ),
            )
            self.dev_db = True if "devtools" in self.app.features else False

            if "devtools" not in self.app.features and not Database.backup_done:
                self._backup_database()

        Base.metadata.create_all(Database.engine)
        logger.info("Connected to database successfully!")

    # ======================== Backups/Reverts ========================

    def _backup_database(self) -> None:
        """Creates a backup of the current database into the backups folder"""
        print("Backing up database...")
        logger.info("Backing up database...")
        now = Arrow.now()
        db_path = os.path.join(APP_FOLDER_PATH, DB_FILE_NAME)
        logger.debug("Production Database Path: " + db_path)

        if not os.path.exists(BACKUPS_FOLDER):
            os.makedirs(BACKUPS_FOLDER)

        db_backup_filename = (
            f"budgetize-backup-{now.format('DD-MM-YYYY (HH.mm)')}.sqlite"
        )
        logger.debug("Backup filename: " + db_backup_filename)

        with open(db_path, mode="rb") as original_db:
            with open(
                os.path.join(BACKUPS_FOLDER, db_backup_filename),
                mode="wb",
            ) as backup:
                backup.write(original_db.read())

        Database.backup_done = True
        logger.info("Backed up database successfully!")

    def revert_from_backup(self, backup_file: Path) -> bool:
        """Reverts the database to the specified backup file."""

        # Close connections to the current database.
        Database.engine.dispose()
        Database.engine = None

        # Write backup file to the database file

        contents: bytes

        with open(backup_file, mode="rb") as f:
            contents = f.read()

        db_path = os.path.join(APP_FOLDER_PATH, DB_FILE_NAME)
        with open(db_path, mode="wb") as f:
            f.write(contents)

        self._init_connection()
        return True

    # ======================== GET INFO ========================

    def get_transactions_from_account(self, account_id: int) -> Iterator[Transaction]:
        """Returns an iterator of transactions from the specified account.

        Args:
        ----
            account_id (int): The ID of the account.

        Yields:
        ------
            Transaction: A transaction from the specified account.

        """
        stmt = select(Transaction).where(Transaction.account_id == account_id)

        with Session(Database.engine) as session:
            for transaction in session.scalars(stmt):
                yield transaction

    def get_monthly_transactions_from_account(
        self,
        account_id: int,
        month: str,
        year: str,
    ) -> Iterator[Transaction]:
        """Returns an iterator of transactions from the specified account within the specified month and year.

        Args:
        ----
            account_id (int): The ID of the account.
            month (str): The month in format 'MM'.
            year (str): The year in format 'YYYY'.

        Yields:
        ------
            Transaction: A transaction from the specified account within the specified month and year.

        """
        transactions = self.get_transactions_from_account(account_id)

        # Filter transactions by month and year
        for transaction in transactions:
            date = Arrow.fromtimestamp(transaction.timestamp)

            if date.format("M") == month and date.format("YYYY") == year:
                yield transaction

    def get_accounts(self) -> Iterator[Account]:
        """Returns an iterator of all accounts.

        Yields
        ------
            Account: An account from the database.

        """
        stmt = select(Account)

        with Session(Database.engine) as session:
            for account in session.scalars(stmt):
                yield account

    def get_account_by_id(self, account_id: int) -> Account:
        """Returns the account with the specified ID.

        Args:
        ----
            account_id (int): The ID of the account.

        Returns:
        -------
            Account: The account with the specified ID.

        """
        with Session(Database.engine) as session:
            found_account: Account = session.get_one(Account, account_id)
            return found_account

    def get_account_by_name(self, name: str) -> Account:
        """Returns the account with the specified name.

        Args:
        ----
            name (str): The name of the account.

        Returns:
        -------
            Account: The account with the specified name.

        """
        with Session(Database.engine) as session:
            stmt = select(Account).where(Account.name == name)
            account: Account = session.execute(stmt).scalars().first()  # type:ignore
            return account

    def account_name_exists(self, name: str) -> bool:
        """Returns True if an account with the specified name exists, False otherwise.

        Args:
        ----
            name (str): The name of the account.

        Returns:
        -------
            bool: True if an account with the specified name exists, False otherwise.

        """
        with Session(Database.engine) as session:
            stmt = select(Account).where(Account.name == name)
            account = session.execute(stmt).scalars().first()
            return account is not None

    def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        """Returns the transaction with the specified ID.

        Args:
        ----
            transaction_id (int): The ID of the transaction.

        Returns:
        -------
            Transaction: The transaction with the specified ID.

        """
        with Session(Database.engine) as session:
            found_transaction: Transaction = session.get_one(
                Transaction,
                transaction_id,
            )
            return found_transaction

    def get_all_recent_transactions(self) -> list[Transaction]:
        """Returns a list with the last 5 transactions saved across all accounts.

        Returns:
            list[Transaction]: A list of recent transactions.
        """
        with Session(Database.engine) as session:
            stmt = (
                select(Transaction)
                .where(Transaction.visible == True)
                .order_by(Transaction.timestamp.desc())
                .limit(5)
            )
            transactions: list[Transaction] = session.execute(stmt).scalars().all()  # type: ignore
            return transactions

    def get_account_balance(self, account_id: int) -> float:
        """Returns the balance of the specified account.

        Args:
            account_id (int): The ID of the account.

        Returns:
            float: The balance of the account.
        """

        stmt = select(Transaction).where(Transaction.account_id == account_id)
        with Session(Database.engine) as session:
            transactions = session.execute(stmt).scalars().all()

            balance = 0.0
            for transaction in transactions:
                balance += transaction.amount

            return balance

    async def get_monthly_income(self) -> float:
        """(Coroutine) Returns the total income for the current month.

        Returns:
            float: The total income for the current month.
        """
        now = Arrow.now()

        income = 0.0
        for account in self.get_accounts():
            for transaction in self.get_monthly_transactions_from_account(
                account.id, now.format("M"), now.format("YYYY")
            ):
                if transaction.amount > 0 and transaction.visible:
                    income += await self.get_amount_in_base_currency(
                        amount=transaction.amount, currency=account.currency
                    )

        return round(income, 2)

    async def get_monthly_expense(self) -> float:
        """(Coroutine) Returns the total expenses for the current month.

        Returns:
            float: The total expenses for the current month.
        """
        now = Arrow.now()

        expense = 0.0
        for account in self.get_accounts():
            for transaction in self.get_monthly_transactions_from_account(
                account.id, now.format("M"), now.format("YYYY")
            ):
                if transaction.amount < 0 and transaction.visible:
                    expense += await self.get_amount_in_base_currency(
                        amount=transaction.amount, currency=account.currency
                    )

        return round(expense, 2)

    async def get_amount_in_base_currency(self, amount: float, currency: str) -> float:
        """(Coroutine) Returns the amount in the base currency.

        Args:
            amount (float): The amount to convert.
            currency (str): The currency of the amount.

        Returns:
            float: The amount in the base currency.
        """
        if currency == self.settings.get_base_currency():
            return amount

        exchange_rate = await CurrencyManager(
            self.settings.get_base_currency()
        ).get_exchange(currency)
        return amount / exchange_rate

    # ======================== ADD/UPDATE INFO ========================

    def add_account(
        self,
        name: str,
        currency: str,
        starting_balance: float,
    ) -> None:
        """Adds a new account to the user.

        Args:
        ----
            name (str): The name of the account.
            currency (str): The currency of the account.
            starting_balance (float): The starting balance of the account.
            account_type_name (str): The type of the account.

        """
        with Session(Database.engine) as session:
            new_account = Account(name=name, currency=currency)
            session.add(new_account)
            session.commit()

            initial_balance_transaction = Transaction(
                account_id=new_account.id,
                amount=starting_balance,
                description="Initial balance",
                category="-",
                timestamp=Arrow.now().timestamp(),
                visible=False,
            )
            session.add(initial_balance_transaction)
            session.commit()

    def add_transaction(
        self,
        account_id: int,
        amount: float,
        description: str,
        category: str,
        timestamp: float,
        visible: bool = True,
    ) -> None:
        """Registers a new transaction.

        Args:
        ----
            account_id (int): The ID of the account.
            amount (float): The amount of the transaction.
            description (str): The description of the transaction.
            category (str): The category of the transaction.
            timestamp (float): The timestamp of the transaction.

        """
        transaction = Transaction(
            account_id=account_id,
            amount=amount,
            description=description,
            category=category,
            timestamp=timestamp,
            visible=visible,
        )

        with Session(Database.engine) as session:
            session.add(transaction)
            session.commit()

    def update_transaction(
        self,
        transaction_id: int,
        account_id: int,
        amount: float,
        description: str,
        category: str,
        timestamp: float,
    ) -> None:
        """Updates the specified transaction in the database.

        Args:
        ----
            transaction_id (int): The ID of the transaction to update.
            account_id (int): The ID of the account.
            amount (float): The new amount of the transaction.
            description (str): The new description of the transaction.
            category (str): The new category of the transaction.
            timestamp (float): The new timestamp of the transaction.

        """
        values = {
            "account_id": account_id,
            "amount": amount,
            "description": description,
            "category": category,
            "timestamp": timestamp,
        }

        logger.info(f"Updating transaction with values: {values}")
        with Session(Database.engine) as session:
            upd = (
                update(Transaction)
                .values(values)
                .where(Transaction.id == transaction_id)
            )
            session.execute(upd)
            session.commit()

    def delete_account(self, account_id: int) -> None:
        """Deletes the specified account from the database.

        Args:
        ----
            account_id (int): The ID of the account to delete.

        """
        stmt = select(Account).where(Account.id == account_id)

        with Session(Database.engine) as session:
            res = session.execute(stmt)

            row = res.fetchone()
            if row is None:
                return

            account = row.tuple()[0]
            session.delete(account)

            # Delete transactions from the account
            transaction_stmt = select(Transaction).where(
                Transaction.account_id == account_id,
            )
            transaction_rows = session.execute(transaction_stmt).fetchall()

            for transaction in transaction_rows:
                transaction_obj = transaction.tuple()[0]
                session.delete(transaction_obj)

            session.commit()

    def delete_transaction(self, transaction_id: int) -> Transaction:
        """Deletes the specified transaction from the DB and returns it.

        Args:
            transaction_id (int): The ID of the transaction to delete.

        Returns:
            Transaction: The deleted transaction.
        """
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        with Session(Database.engine) as session:
            res = session.execute(stmt)
            row = res.fetchone()

            selected_transaction: Transaction = row.tuple()[0]  # type: ignore
            session.delete(selected_transaction)
            session.commit()
            return selected_transaction
