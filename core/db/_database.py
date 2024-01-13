from typing import Iterator

from arrow import Arrow
from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.orm import Session

from core.consts import DB_URL

from .orm import Account, Base, Transaction


class Database:
    engine = create_engine(DB_URL, echo=True)

    def __init__(self):
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
        """Returns an iterator of transactions from the specified account within the specified month and year"""
        transactions = self.get_transactions_from_account(account_id)

        # Filter transactions by month and year
        with Session(Database.engine) as session:
            for transaction in transactions:
                date = Arrow.fromtimestamp(transaction.datetime)
                if date.month == month and date.year == year:
                    yield transaction

    def get_accounts(self) -> Iterator[Account]:
        """Returns an iterator of all accounts"""
        stmt = select(Account)

        with Session(Database.engine) as session:
            for account in session.scalars(stmt):
                yield account

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
