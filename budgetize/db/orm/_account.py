"""Account ORM model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ._account_type import AccountType
from ._base import Base


class Account(Base):
    """ORM model for the accounts table. Represents a financial account for the user."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str]
    account_type_name: Mapped[str]
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[float]

    def __repr__(self) -> str:
        """String representation of the Account object."""

        return (
            f"<Account(id={self.id}, name={self.name}, account_type_name={self.account_type_name}, "
            f"currency={self.currency}, balance={self.balance})>"
        )

    @property
    def account_type(self) -> AccountType:
        """Returns the account type as an enum object."""
        return AccountType[self.account_type_name]
