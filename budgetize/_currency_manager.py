"Module that handles requests to the currency exchanges API"
import json
import os
import traceback
from typing import Optional, TypedDict

import httpx
from arrow import Arrow
from bs4 import BeautifulSoup

from budgetize.consts import APP_FOLDER_PATH, VALID_EXCHANGE_TIMESTAMP


class RatesData(TypedDict):
    """Dict that represents how are curreny data saved."""

    retrieve_timestamp: int
    rate: float


class CurrencyManager:
    """Class that handles requests to the currency exchanges API and saves it to disk"""

    """
    !Format for saving exchange rates

    {main_currency}: {
        {currency}: {
            "retrieve_timestamp": {timestamp},
            "rate": {rate}
    }

    Example

    USD: {
        EUR: {
            "retrieve_timestamp": 00000000,
            "rate": 0.8        
        }
    }
    """

    def __init__(self, base_currency: str):
        """
        Creates a new CurrencyManager object.

        Retrieves currency exchanges using requests with Google search
        """

        self.FILE_PATH = os.path.join(APP_FOLDER_PATH, "currency_exchanges.json")
        self.base_currency = base_currency

    async def update_invalid_rates(self) -> bool:
        """(Coroutine) Updates all the rates that have expired. Returns True if successful."""

        rates = self._get_all_local_rates()
        if not rates:
            return True

        for base_currency, data in rates[self.base_currency].items():
            if self.has_expired(data["retrieve_timestamp"]):
                exchange = await self._request_exchange(base_currency)
                if exchange < 0:
                    return False
                else:
                    self._save_exchange(self.base_currency, base_currency, exchange)

        return True

    def has_expired_rates(self) -> bool:
        """Returns True if there is a rate that has expired."""

        rates = self._get_all_local_rates()
        if not rates:
            return False

        for currency, data in rates[self.base_currency].items():
            if self.has_expired(data["retrieve_timestamp"]):
                return True
        return False

    async def update_rate(self, currency: str) -> float:
        """Forces a currency rate update."""
        exchange = await self._request_exchange(currency)
        if exchange < 0:
            return -1
        self._save_exchange(self.base_currency, currency, exchange)
        return exchange

    async def get_exchange(self, currency: str) -> float:
        """
        Retrieves the exchange rate between the base currency and the given currency.

        Args:
            currency (str): The currency to convert to

        Returns:
            float: The exchange rate
        """

        rates = self._get_all_local_rates()
        if not rates:
            return await self.update_rate(currency)

        if self.base_currency not in rates or currency not in rates[self.base_currency]:
            return await self.update_rate(currency)

        rate_data = rates[self.base_currency][currency]

        # If the exchange rate is older than 1 week, retrieve it again
        if self.has_expired(rate_data["retrieve_timestamp"]):
            return await self.update_rate(currency)

        return rates[self.base_currency][currency]["rate"]

    def has_expired(self, timestamp: int) -> bool:
        """
        Checks if the timestamp has expired.

        Args:
            timestamp (int): The timestamp to check

        Returns:
            bool: True if the timestamp has expired, False otherwise
        """

        return timestamp > Arrow.now().timestamp() + VALID_EXCHANGE_TIMESTAMP

    async def _request_exchange(self, currency: str) -> float:
        """
        (Coroutine) Retrieves the exchange rate between the base currency and the given currency.

        Args:
            currency (str): The currency to convert to

        Returns:
            float: The exchange rate
        """

        try:
            async with httpx.AsyncClient() as client:

                url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={self.base_currency.upper()}&To={currency.upper()}"
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50",
                }
                r = await client.get(url, timeout=15)
                print(r.text)
                soup = BeautifulSoup(r.text, "html.parser")
                a = soup.find("p", class_="result__BigRate-sc-1bsijpp-1 dPdXSB")
                rate: float = float(a.text.split(" ")[0])  # type: ignore

                return rate
        except Exception:
            traceback.print_exc()
            return -1.0

    def _get_all_local_rates(self) -> Optional[dict[str, dict[str, RatesData]]]:
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

        rates = self._get_all_local_rates()

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

        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(rates, f, indent=4)
