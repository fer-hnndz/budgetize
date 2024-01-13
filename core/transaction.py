from arrow.arrow import Arrow


class Transaction:
    def __init__(self, account: int, amount: float, date: Arrow):
        self.account: int = account
        self.amount = amount
        self.date = date

    @classmethod
    def from_data_file(cls, data: dict):
        return Transaction(
            data["account"],
            data["amount"],
            Arrow.fromtimestamp(data["date"]),
        )

    def to_data_file(self) -> dict:
        return {
            "account": self.account,
            "amount": self.amount,
            "date": self.date.timestamp,
        }
