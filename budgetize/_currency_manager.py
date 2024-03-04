"Module that handles requests to the currency exchanges API"
import json
import os
from typing import Optional, TypedDict

import requests
from arrow import Arrow
from bs4 import BeautifulSoup

from budgetize.consts import APP_FOLDER_PATH, VALID_EXCHANGE_TIMESTAMP


class RatesData(TypedDict):
    """Dict that represents how are curreny data saved."""

    retrieve_timestamp: int
    rate: float


class CurrencyManager:
    """Class that handles requests to the currency exchanges API and saves it to disk"""

    def __init__(self, base_currency: str):
        """
        Creates a new CurrencyManager object.

        Retrieves currency exchanges using requests with Google search
        """

        self.FILE_PATH = os.path.join(APP_FOLDER_PATH, "currency_exchanges.json")
        self.base_currency = base_currency

    def request_exchange(self, currency: str) -> float:
        """
        Retrieves the exchange rate between the base currency and the given currency.

        Args:
            currency (str): The currency to convert to

        Returns:
            float: The exchange rate
        """

        url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={self.base_currency.upper()}&To={currency.upper()}"
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        a = soup.find("p", class_="result__BigRate-sc-1bsijpp-1 dPdXSB")
        rate: float = float(a.text.split(" ")[0])  # type: ignore

        return rate

    def get_local_rates(self) -> Optional[dict[str, dict[str, RatesData]]]:
        """
        Retrieves the exchange rates from a local file.

        Returns:
            dict: The exchange rates
        """

        if not os.path.exists(self.FILE_PATH):
            return {}

        with open(self.FILE_PATH, "r", encoding="UTF-8") as f:
            rates: dict[str, dict[str, RatesData]] = json.load(f)

        return rates

    def get_exchange(self, currency: str) -> float:
        """
        Retrieves the exchange rate between the base currency and the given currency.

        Args:
            currency (str): The currency to convert to

        Returns:
            float: The exchange rate
        """

        rates = self.get_local_rates()
        if not rates:
            rate = self.request_exchange(currency)
            self._save_exchange(self.base_currency, currency, rate)
            return rate

        if self.base_currency not in rates or currency not in rates[self.base_currency]:
            exchange = self.request_exchange(currency)
            self._save_exchange(self.base_currency, currency, exchange)
            return exchange

        rate_data = rates[self.base_currency][currency]

        # If the exchange rate is older than 1 week, retrieve it again
        if (
            rate_data["retrieve_timestamp"]
            < Arrow.now().timestamp() - VALID_EXCHANGE_TIMESTAMP
        ):
            exchange = self.request_exchange(currency)
            self._save_exchange(self.base_currency, currency, exchange)
            return exchange

        return rates[self.base_currency][currency]["rate"]

    def _save_local_rates(self, rates: dict) -> None:
        """
        Saves the exchange rates to a local file.

        Args:
            rates (dict): The exchange rates
        """

        file_path = os.path.join(APP_FOLDER_PATH, "currency_exchanges.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rates, f, indent=4)

    def _save_exchange(
        self, base_currency: str, currency: str, exchange: float
    ) -> None:
        """
        Saves the exchange rate between the base currency and the given currency to disk.

        Args:
            base_currency (str): The base currency
            currency (str): The currency to convert to
            exchange (float): The exchange rate
        """

        rates = self.get_local_rates()

        # In case the rates file is not created.
        if not rates:
            rates = {
                base_currency: {
                    currency: {
                        "retrieve_timestamp": round(Arrow.now().timestamp()),
                        "rate": exchange,
                    }
                }
            }

            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(rates, f, indent=4)

            return

        if base_currency not in rates:
            rates[base_currency] = {}

        rates[base_currency][currency] = {
            "retrieve_timestamp": round(Arrow.now().timestamp()),
            "rate": exchange,
        }
