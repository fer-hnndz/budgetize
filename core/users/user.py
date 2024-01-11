from typing import List

from core.accounts.account import Account


class User:
    def __init__(self, name: str, base_currency: str, accounts: List[Account]):
        """Represents a user of the app"""
        self.name: str = name
        self.base_currency: str = base_currency
        self.accounts: List[Account] = accounts

    @classmethod
    def from_file_data(cls, data: dict):
        return User(
            data["name"],
            data["base_currency"],
            [Account.from_file_data(account) for account in data["accounts"]],
        )

    def to_dict(self) -> dict:
        """Returns the data of the user as a dict to write it to a file"""
        return {
            "name": self.name,
            "base_currency": self.base_currency,
            "accounts": [account.to_file_data() for account in self.accounts],
        }
