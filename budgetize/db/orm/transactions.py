"""Database ORM for transactions table."""

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class Transaction(Base):  # pylint: disable=too-few-public-methods
    """Database ORM for transactions table. Represents a transaction on an account."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[Optional[str]] = mapped_column(ForeignKey("accounts.id"))
    amount: Mapped[float]
    description: Mapped[Optional[str]] = mapped_column(String(255))
    category: Mapped[str]
    timestamp: Mapped[float]

    # If its visible it will contribute to balance and expenses. If not, its an hidden expense. For example the initial balance or transfers
    visible: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        """String representation of the Transaction object."""

        return f"""<Transaction(
        id={self.id}, 
        account_id={self.account_id}, 
        amount={self.amount}, 
        description={self.description}, 
        category={self.category}
        timestamp={self.timestamp})>"""
