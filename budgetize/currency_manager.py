"Module that handles requests to the currency exchanges API"
import json
import os
import traceback
from typing import Optional, TypedDict

import httpx
from arrow import Arrow
from bs4 import BeautifulSoup
from httpx import HTTPStatusError, NetworkError, TimeoutException

from budgetize.consts import APP_FOLDER_PATH, VALID_EXCHANGE_TIMESTAMP
from budgetize.exceptions import ExchangeRateFetchError


class RatesData(TypedDict):
    """Dict that represents how are curreny data saved."""

    retrieve_timestamp: int
    rate: float


class CurrencyManager:
    """Class that handles requests to the currency exchanges API and saves it to disk"""

    # {main_currency}: {
    #     {currency}: {
    #         "retrieve_timestamp": {timestamp},
    #         "rate": {rate}
    # }

    # Example

    # USD: {
    #     EUR: {
    #         "retrieve_timestamp": 00000000,
    #         "rate": 0.8
    #     }
    # }
    #

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

        if self.base_currency not in rates.values():
            rates[self.base_currency] = {}

        for base_currency, data in rates[self.base_currency].items():
            if self.has_expired(data["retrieve_timestamp"]):
                exchange = await self._request_exchange(base_currency)
                if exchange < 0:
                    return False

                self._save_exchange(self.base_currency, base_currency, exchange)

        return True

    def has_expired_rates(self) -> bool:
        """Returns True if there is a rate that has expired."""

        rates = self._get_all_local_rates()
        if not rates:
            return False

        if not self.base_currency in rates.values():
            return True

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

        if (
            self.base_currency not in rates.values()
            or currency not in rates[self.base_currency].values()
        ):
            return await self.update_rate(currency)

        rate_data = rates[self.base_currency][currency]

        # If the exchange rate is older than 1 week, retrieve it again

        try:
            if self.has_expired(rate_data["retrieve_timestamp"]):
                return await self.update_rate(currency)

            return rates[self.base_currency][currency]["rate"]
        except ExchangeRateFetchError:
            return rate_data["rate"]

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

        async with httpx.AsyncClient() as client:

            url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={self.base_currency.upper()}&To={currency.upper()}"

            try:
                r = await client.get(url, timeout=8)

                soup = BeautifulSoup(r.text, "html.parser")

                main_element = soup.find("main")
                if not main_element:
                    raise ExchangeRateFetchError(
                        "Could not find main element in response html."
                    )

                digits_span = soup.find("span", class_="faded-digits")

                if digits_span is None:
                    return -1

                digits_str: str = digits_span.get_text()
                parent_div = digits_span.parent  # type:ignore

                # Get first element of the iterator
                for child in parent_div.children:  # type:ignore
                    rate_p = str(child)
                    break

                amount_of_zero = len(rate_p.split(".")[-1])
                digits_to_sum = ("0." + ("0" * amount_of_zero)) + digits_str
                return float(rate_p) + float(digits_to_sum)

            except TimeoutException as e:
                raise ExchangeRateFetchError(
                    f"The request timed out fetching the exchange rate for {currency.upper()}.\n{traceback.format_exc()}"
                ) from e
            except NetworkError as e:
                raise ExchangeRateFetchError(
                    f"A network error has ocurred trying to fetch the exchange rate for {currency.upper()}.\nPlease check your internet connection."
                ) from e
            except HTTPStatusError:
                raise ExchangeRateFetchError(
                    f"Server responded with an error when fetching exchange rate for {currency.upper()}.\n{traceback.format_exc()}"
                )
            except Exception as e:
                raise ExchangeRateFetchError(
                    f"An unkown error has ocurred trying to fetch the exchange rate for {currency.upper()}.\n{traceback.format_exc()}"
                ) from e

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
