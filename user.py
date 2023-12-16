from typing import List
from account import Account


class User:
    def __init__(self, id: int, name: str, surname: str, accounts: List[Account]):
        self.id: int = id
        self.name: str = name
        self.surname: str = surname
        self.accounts: List[Account] = accounts

    @classmethod
    def from_file_data(cls, data: dict):
        return User(
            data["id"],
            data["name"],
            data["surname"],
            [Account.from_file_data(account) for account in data["accounts"]],
        )

    def get_data_file_content(self) -> dict:
        """Returns the data of the user as a dict to write it to a file"""
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "accounts": [account.to_file_data() for account in self.accounts],
        }
