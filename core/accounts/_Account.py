from typing import List

from core.Transaction import Transaction

from ._AccountType import AccountType


class Account:
    def __init__(
        self,
        #       account_id: int,
        name: str,
        account_type: AccountType,
        balance: float,
        currency: str,
        transactions: list[Transaction] = [],
    ):
        # self.id = account_id
        self.name: str = name
        self.account_type: AccountType = account_type
        self.currency = currency
        self.balance: float = balance
        self.transactions: List[Transaction] = transactions

    @classmethod
    def from_file_data(cls, data: dict):
        return Account(
            # data["id"],
            name=data["name"],
            account_type=AccountType[data["account_type"]],
            currency=data["currency"],
            balance=data["balance"],
            transactions=[
                Transaction.from_data_file(transaction)
                for transaction in data["transactions"]
            ],
        )

    def to_file_data(self) -> dict:
        return {
            # "id": self.id,
            "name": self.name,
            "account_type": self.account_type.name,
            "currency": self.currency,
            "balance": self.balance,
            "transactions": [
                transaction.to_data_file() for transaction in self.transactions
            ],
        }
