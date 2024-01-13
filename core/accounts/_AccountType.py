from enum import Enum, auto


class AccountType(Enum):
    EMERGENCY = auto()
    SAVINGS = auto()
    WALLET = auto()
    CHECKING = auto()
    INVESTMENT = auto()
