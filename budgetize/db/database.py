"""Definition of Database class that handles database operations"""

from typing import Iterator

from arrow import Arrow
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from textual.app import App

from budgetize import CurrencyManager, SettingsManager
from budgetize.consts import PROD_DB_URL
from budgetize.db.orm._base import Base
from budgetize.db.orm.account import Account
from budgetize.db.orm.transactions import Transaction


class Database:
    """This class is the API for interacting with the database.
    All read and writes are done here which may include utilities for converting currencies, for example.
    """

    engine = create_engine(PROD_DB_URL)

    def __init__(self, app: App):
        """Initializes a Database instance.

        Args:
            app (App): The application instance.
        """
        if app is None:
            raise RuntimeError(app, "App cannot be None")

        Database.engine = create_engine(
            PROD_DB_URL
            if not "devtools" in app.features
            else "sqlite:///test_db.sqlite"
        )
        Base.metadata.create_all(self.engine)
        self.settings = SettingsManager()

    def get_transactions_from_account(self, account_id: int) -> Iterator[Transaction]:
        """Returns an iterator of transactions from the specified account.

        Args:
            account_id (int): The ID of the account.

        Yields:
            Transaction: A transaction from the specified account.
        """
        stmt = select(Transaction).where(Transaction.account_id == account_id)

        with Session(Database.engine) as session:
            for transaction in session.scalars(stmt):
                yield transaction

    def get_monthly_transactions_from_account(
        self, account_id: int, month: str, year: str
    ) -> Iterator[Transaction]:
        """Returns an iterator of transactions from the specified account within the specified month and year.

        Args:
            account_id (int): The ID of the account.
            month (str): The month in format 'MM'.
            year (str): The year in format 'YYYY'.

        Yields:
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

        Yields:
            Account: An account from the database.
        """
        stmt = select(Account)

        with Session(Database.engine) as session:
            for account in session.scalars(stmt):
                yield account

    def get_account_by_id(self, account_id: int) -> Account:
        """Returns the account with the specified ID.

        Args:
            account_id (int): The ID of the account.

        Returns:
            Account: The account with the specified ID.
        """
        with Session(Database.engine) as session:
            found_account: Account = session.get_one(Account, account_id)
            return found_account

    def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        """Returns the transaction with the specified ID.

        Args:
            transaction_id (int): The ID of the transaction.

        Returns:
            Transaction: The transaction with the specified ID.
        """
        with Session(Database.engine) as session:
            found_transaction: Transaction = session.get_one(
                Transaction, transaction_id
            )
            return found_transaction

    def add_account(self, account: Account) -> None:
        """Adds a new account to the user.

        Args:
            account (Account): The account to be added.
        """
        with Session(Database.engine) as session:
            session.add(account)
            session.commit()

    def add_transaction(
        self,
        account_id: int,
        amount: float,
        description: str,
        category: str,
        timestamp: float,
    ) -> None:
        """Registers a new transaction.

        Args:
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
        )

        with Session(Database.engine) as session:
            session.add(transaction)

            # Update the account balance
            account = session.get_one(Account, account_id)
            account.balance += float(amount)
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

        with Session(Database.engine) as session:
            upd = (
                update(Transaction)
                .values(values)
                .where(Transaction.id == transaction_id)
            )
            session.execute(upd)
            session.commit()

    def get_all_recent_transactions(self) -> list[Transaction]:
        """Returns a list with the last 5 transactions saved across all accounts.

        Returns:
            list[Transaction]: A list of recent transactions.
        """
        with Session(Database.engine) as session:
            stmt = select(Transaction).order_by(Transaction.timestamp.desc()).limit(5)
            transactions: list[Transaction] = session.execute(stmt).scalars().all()  # type: ignore
            return transactions

    async def get_monthly_income(self) -> float:
        """(Coroutine) Returns the total income for the current month.

        Returns:
            float: The total income for the current month.
        """
        now = Arrow.now()

        income = 0.0
        for account in self.get_accounts():

            exchange_rate = 1.0
            if account.currency != self.settings.get_base_currency():
                exchange_rate = await CurrencyManager(
                    self.settings.get_base_currency()
                ).get_exchange(account.currency)

            for transaction in self.get_monthly_transactions_from_account(
                account.id, now.format("M"), now.format("YYYY")
            ):
                if transaction.amount > 0:
                    income += transaction.amount / exchange_rate

        return round(income, 2)

    def delete_account(self, account_id: int) -> None:
        """Deletes the specified account from the database.

        Args:
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
                Transaction.account_id == account_id
            )
            transaction_rows = session.execute(transaction_stmt).fetchall()

            for transaction in transaction_rows:
                transaction_obj = transaction.tuple()[0]
                session.delete(transaction_obj)

            session.commit()

    async def get_monthly_expense(self) -> float:
        """(Coroutine) Returns the total expenses for the current month.

        Returns:
            float: The total expenses for the current month.
        """
        now = Arrow.now()

        expense = 0.0
        for account in self.get_accounts():
            rate = 1.0
            if account.currency != self.settings.get_base_currency():
                rate = await CurrencyManager(
                    self.settings.get_base_currency()
                ).get_exchange(account.currency)
            for transaction in self.get_monthly_transactions_from_account(
                account.id, now.format("M"), now.format("YYYY")
            ):
                if transaction.amount < 0:
                    expense += transaction.amount / rate

        return round(expense, 2)

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
