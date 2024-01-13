from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[float] = mapped_column(nullable=False)

    def __repr__(self):
        return (
            f"Account(id={self.id}, currency={self.currency}, balance={self.balance})"
        )
