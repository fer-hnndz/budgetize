"""Database ORM for transactions table."""
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class Transaction(Base):  # pylint: disable=too-few-public-methods
    """Database ORM for transactions table. Represents a transaction on an account."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    account_id: Mapped[Optional[str]] = mapped_column(ForeignKey("accounts.id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    timestamp: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self):
        return """<Transaction(
        id={self.id}, 
        account_id={self.account_id}, 
        currency={self.currency}, 
        balance={self.balance}, 
        datetime={self.datetime})>"""
