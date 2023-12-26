from typing import List

from core.accounts.AccountType import AccountType
from core.transaction import Transaction


class Account:
    def __init__(
        self,
        #       account_id: int,
        name: str,
        #        account_type: AccountType,
        #        owner_id: int,
        balance: float,
        transactions: list[Transaction] = [],
    ):
        # self.id = account_id
        self.name: str = name
        # self.account_type: AccountType = account_type
        # self.owner_id: int = owner_id
        self.balance: float = balance
        self.transactions: List[Transaction] = transactions

    @classmethod
    def from_data_file(cls, data: dict):
        return Account(
            # data["id"],
            data["name"],
            # AccountType[data["account_type"]],
            # data["owner_id"],
            data["balance"],
            [
                Transaction.from_data_file(transaction)
                for transaction in data["transactions"]
            ],
        )

    def to_file_data(self) -> dict:
        return {
            # "id": self.id,
            "name": self.name,
            # "account_type": self.account_type.name,
            # "owner_id": self.owner_id,
            "balance": self.balance,
            "transactions": [
                transaction.to_data_file() for transaction in self.transactions
            ],
        }
