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
    amount: Mapped[float]
    description: Mapped[Optional[str]] = mapped_column(String(255))
    category: Mapped[str]
    timestamp: Mapped[float]

    def __repr__(self):
        return f"""<Transaction(
        id={self.id}, 
        account_id={self.account_id}, 
        amount={self.amount}, 
        description={self.description}, 
        category={self.category}
        timestamp={self.timestamp})>"""
