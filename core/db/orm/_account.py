from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ._account_type import AccountType
from ._base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str]
    _account_type_name: Mapped[str]
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[float]

    def __repr__(self):
        return (
            f"<Account(id={self.id}, name={self.name}, account_type={self.account_type}, "
            f"currency={self.currency}, balance={self.balance})>"
        )

    @property
    def account_type(self) -> AccountType:
        return AccountType[self._account_type_name]
