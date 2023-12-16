from arrow.arrow import Arrow


class Transaction:
    def __init__(self, origin: int, destination: int, amount: float, date: Arrow):
        self.origin: int = origin
        self.destination: int = destination
        self.amount = amount
        self.date = date

    @classmethod
    def from_data_file(cls, data: dict):
        return Transaction(
            data["origin"],
            data["destination"],
            data["amount"],
            Arrow.fromtimestamp(data["date"]),
        )

    def to_file_data(self) -> dict:
        return {
            "origin": self.origin,
            "destination": self.destination,
            "amount": self.amount,
            "date": self.date.timestamp,
        }
