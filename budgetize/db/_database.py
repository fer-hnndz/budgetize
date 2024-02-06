"""Definition of Database class that handles database operations"""

from typing import Iterator

from arrow import Arrow
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from textual.app import App

from budgetize.consts import PROD_DB_URL

from .orm import Account, Base, Transaction


class Database:
    """Class that handles database operations"""

    engine = create_engine(PROD_DB_URL)

    def __init__(self, app: App):
        if app is None:
            return

        Database.engine = create_engine(
            PROD_DB_URL
            if not "devtools" in app.features
            else "sqlite:///test_db.sqlite"
        )
        Base.metadata.create_all(self.engine)

    def get_transactions_from_account(self, account_id: int) -> Iterator[Transaction]:
        """Returns an iterator of transactions from the specified account"""
        stmt = select(Transaction).where(Transaction.account_id == account_id)

        with Session(Database.engine) as session:
            for transaction in session.scalars(stmt):
                yield transaction

    def get_monthly_transactions_from_account(
        self, account_id: int, month: str, year: str
    ) -> Iterator[Transaction]:
        """
        Returns an iterator of transactions from
        the specified account within the specified month and year
        """
        transactions = self.get_transactions_from_account(account_id)

        # Filter transactions by month and year
        for transaction in transactions:
            date = Arrow.fromtimestamp(transaction.timestamp)
            ar = Arrow.fromtimestamp(transaction.timestamp)
            print("===================================")
            print(f"Date for transaction #{transaction.id}: {ar.format('M/D/YYYY')}")

            print(f"Ar m/y: {ar.format('M')} | {ar.format('YYYY')}")
            print(f"Received: {month} | {year}")

            if date.format("M") == month and date.format("YYYY") == year:
                yield transaction

    def get_accounts(self) -> Iterator[Account]:
        """Returns an iterator of all accounts"""
        stmt = select(Account)

        with Session(Database.engine) as session:
            for account in session.scalars(stmt):
                yield account

    def get_account_by_id(self, account_id: int) -> Account:
        """Returns the account with the specified id"""
        with Session(Database.engine) as session:
            return session.get_one(Account, account_id)

    def add_account(self, account: Account) -> None:
        """Adds a new account to the user"""
        with Session(Database.engine) as session:
            session.add(account)
            session.commit()

    def add_transaction(self, transaction: Transaction) -> None:
        """Registers a new transaction"""

        with Session(Database.engine) as session:
            session.add(transaction)
            session.commit()
