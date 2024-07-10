"""Stores the class that will be used to store exchange rate information."""

from typing import TypeVar

from arrow import Arrow

from budgetize.consts import VALID_EXCHANGE_TIMESTAMP

T = TypeVar("T", bound="ExchangeRate")


class ExchangeRate:
    """Represents a currency's exchange rate information between a base currency.

    Base Currency information can't be stored in this class, as it is not needed.

    Parameters
    ----------
    currency : str
        The currency code of the currency.

    rate : float
        The exchange rate of the currency.

    retrieve_timestamp : int
        The timestamp of when the exchange rate was retrieved.


    Attributes
    ----------
    currency : str
        The currency code of the currency.

    rate : float
        The exchange rate of the currency.

    retrieve_timestamp : int
        The timestamp of when the exchange rate was retrieved.


    """

    def __init__(self, currency: str, rate: float, retrieve_timestamp: int):
        self.currency = currency
        self.rate = rate
        self.retrieve_timestamp = retrieve_timestamp

    def is_expired(self) -> bool:
        """Checks if the exchange rate is expired.
        Rates are expired if the time since the rate was retrieved is greater
        than `budgetize.consts.VALID_EXCHANGE_TIMESTAMP`.

        Returns
        -------
        bool
            True if the exchange rate is expired, False otherwise.

        """
        return (
            Arrow.now().timestamp()
            >= self.retrieve_timestamp + VALID_EXCHANGE_TIMESTAMP
        )

    @classmethod
    def from_dict(cls: type[T], data: dict) -> T:
        """Creates an ExchangeRate object from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the data to create the ExchangeRate object.

        Returns
        -------
        ExchangeRate
            The ExchangeRate object created from the dictionary.

        """
        return cls(
            data.get("currency", ""),
            data.get("rate", 0),
            data.get("retrieve_timestamp", 0),
        )

    def to_dict(self) -> dict:
        """Converts the ExchangeRate object to save its information to the exchange rate file.

        Returns
        -------
        dict
            The dictionary representation of the ExchangeRate object.

        """
        return {
            "rate": self.rate,
            "retrieve_timestamp": self.retrieve_timestamp,
        }

    def __str__(self) -> str:
        return f"ExchangeRate<{self.currency}, {self.rate}, {self.retrieve_timestamp}>"
