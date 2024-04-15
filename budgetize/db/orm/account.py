"""Account ORM model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class Account(Base):
    """ORM model for the accounts table. Represents a financial account for the user."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    currency: Mapped[str] = mapped_column(String(3))

    def __repr__(self) -> str:
        """String representation of the Account object."""

        return f"<Account(id={self.id}, name={self.name}, currency={self.currency})>"
