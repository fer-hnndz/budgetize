from typing import List
from core.accounts.account import Account


class User:
    def __init__(self, name: str, surname: str, accounts: List[Account]):
        self.name: str = name
        self.surname: str = surname
        self.accounts: List[Account] = accounts

    @classmethod
    def from_file_data(cls, data: dict):
        return User(
            data["name"],
            data["surname"],
            [Account.from_file_data(account) for account in data["accounts"]],
        )

    def to_dict(self) -> dict:
        """Returns the data of the user as a dict to write it to a file"""
        return {
            "name": self.name,
            "surname": self.surname,
            "accounts": [account.to_file_data() for account in self.accounts],
        }
