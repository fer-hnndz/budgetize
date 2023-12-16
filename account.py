from enum import Enum
from transaction import Transaction
from typing import List


class AccountType(Enum):
    EMERGENCY = 1
    SAVINGS = 2
    WALLET = 3
    CHECKING = 4
    INVESTMENT = 5


class Account:
    def __init__(
        self,
        account_id: int,
        account_name: str,
        account_type: AccountType,
        owner_id: int,
        balance: float,
        transactions: list[Transaction] = [],
    ):
        self.id = account_id
        self.account_name: str = account_name
        self.account_type: AccountType = account_type
        self.owner_id: int = owner_id
        self.balance: float = balance
        self.transactions: List[Transaction] = transactions

    @classmethod
    def from_data_file(cls, data: dict):
        return Account(
            data["id"],
            data["account_name"],
            AccountType[data["account_type"]],
            data["owner_id"],
            data["balance"],
            [
                Transaction.from_data_file(transaction)
                for transaction in data["transactions"]
            ],
        )

    def to_file_data(self) -> dict:
        return {
            "id": self.id,
            "account_name": self.account_name,
            "account_type": self.account_type.name,
            "owner_id": self.owner_id,
            "balance": self.balance,
            "transactions": [
                transaction.to_data_file() for transaction in self.transactions
            ],
        }
