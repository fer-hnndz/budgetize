"""AccountType Enum."""
from enum import Enum, auto


class AccountType(Enum):
    """Enum for the different types of accounts."""

    EMERGENCY = auto()
    SAVINGS = auto()
    WALLET = auto()
    CHECKING = auto()
    INVESTMENT = auto()
