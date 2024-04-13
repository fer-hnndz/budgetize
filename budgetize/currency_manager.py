"Module that handles requests to the currency exchanges API"
import json
import logging
import os
import traceback
from typing import TypedDict

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
    """Class that handles requests to the currency exchanges API and saves it to disk."""

    CURRENT_RATES: dict[str, dict[str, RatesData]] = {}
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

        Retrieves currency exchanges using requests with Google search.

        Args:
            base_currency (str): The base currency.
        """
        self.file_path = os.path.join(APP_FOLDER_PATH, "currency_exchanges.json")
        self.base_currency = base_currency

    async def update_invalid_rates(self) -> bool:
        """(Coroutine) Updates all the rates that have expired. Returns True if successful."""
        logging.info("Checking for invalid rates...")
        CurrencyManager.CURRENT_RATES = self._get_all_local_rates()
        logging.debug(f"Current rates: {CurrencyManager.CURRENT_RATES}")

        if not CurrencyManager.CURRENT_RATES:
            logging.info("No rates found. Returning True.")
            return True

        if self.base_currency not in CurrencyManager.CURRENT_RATES:
            logging.info("Base currency not found in rates. Creating new dict.")
            CurrencyManager.CURRENT_RATES[self.base_currency] = {}

        for base_currency, data in CurrencyManager.CURRENT_RATES[
            self.base_currency
        ].items():
            if self.has_expired(data["retrieve_timestamp"]):
                logging.info(
                    f"Rate for {self.base_currency}-{base_currency} has expired. Updating..."
                )
                exchange = await self._request_exchange(base_currency)
                if exchange < 0:
                    logging.critical(
                        f"Error fetching exchange rate for {self.base_currency}-{base_currency}. Skipping..."
                    )
                    return False

                logging.info("Saving fetched exchange rate...")
                self._save_exchange(self.base_currency, base_currency, exchange)

        return True

    def has_expired_rates(self) -> bool:
        """Returns True if there is a rate that has expired."""
        rates = self._get_all_local_rates()
        if not rates:
            return False

        if not self.base_currency in rates.values():
            return True

        for _, data in rates[self.base_currency].items():
            if self.has_expired(data["retrieve_timestamp"]):
                return True
        return False

    async def update_rate(self, currency: str) -> float:
        """(Coroutine) Forces a currency rate update."""
        exchange = await self._request_exchange(currency)
        if exchange < 0:
            return -1
        self._save_exchange(self.base_currency, currency, exchange)
        return exchange

    async def get_exchange(self, currency: str) -> float:
        """
        (Coroutine) Retrieves the exchange rate between the base currency and the given currency.

        Args:
            currency (str): The currency to convert to.

        Returns:
            float: The exchange rate.
        """

        logging.info(f"Retrieving exchange rate for {self.base_currency}-{currency}...")
        if not CurrencyManager.CURRENT_RATES:
            logging.info("Currency dict is empty. Updating from local...")

            CurrencyManager.CURRENT_RATES = self._get_all_local_rates()
            if not CurrencyManager.CURRENT_RATES:
                logging.info(
                    "CURRENT_RATES dict is still empty after fetching from local rates, fetching online..."
                )
                return await self.update_rate(currency)

        if self.base_currency not in CurrencyManager.CURRENT_RATES:
            logging.info("Base currency not found in local rates. Updating...")
            return await self.update_rate(currency)

        if CurrencyManager.CURRENT_RATES[self.base_currency] == {}:
            logging.info("Base currency dict is empty. Updating from local...")
            CurrencyManager.CURRENT_RATES = self._get_all_local_rates()
            logging.info(f"Retrieved local rates: {CurrencyManager.CURRENT_RATES}")

        if currency not in CurrencyManager.CURRENT_RATES[self.base_currency].keys():
            logging.info("Currency not found in local rates. Updating...")
            return await self.update_rate(currency)

        rate_data = CurrencyManager.CURRENT_RATES[self.base_currency][currency]

        # If the exchange rate is older than 1 week, retrieve it again

        try:
            if self.has_expired(rate_data["retrieve_timestamp"]):
                logging.info("Currency rate has expired. Updating...")
                return await self.update_rate(currency)

            logging.info("Currency rate found in local rates. Returning local")
            return CurrencyManager.CURRENT_RATES[self.base_currency][currency]["rate"]
        except ExchangeRateFetchError:
            logging.critical("Error fetching currency rate. Returning current")
            return rate_data["rate"]

    def has_expired(self, timestamp: int) -> bool:
        """
        Checks if the timestamp has expired.

        Args:
            timestamp (int): The timestamp to check.

        Returns:
            bool: True if the timestamp has expired, False otherwise.
        """
        return timestamp > Arrow.now().timestamp() + VALID_EXCHANGE_TIMESTAMP

    def _save_last_html_response(self, response: str) -> None:
        """Saves last HTML in a file"""

        with open(
            os.path.join(APP_FOLDER_PATH, "last_html_response.html"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(response)

    async def _request_exchange(self, currency: str) -> float:
        """
        (Coroutine) Retrieves the exchange rate between the base currency and the given currency.

        Args:
            currency (str): The currency to convert to.

        Returns:
            float: The exchange rate.
        """
        async with httpx.AsyncClient() as client:

            url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={self.base_currency.upper()}&To={currency.upper()}"
            logging.info(f"Attempting to fetch exchange rate at {url}")
            try:
                r = await client.get(url, timeout=8)
                logging.debug(f"Response status code: {r.status_code}")
                logging.info("Saving response HMTL...")
                self._save_last_html_response(r.text)

                soup = BeautifulSoup(r.text, "html.parser")

                main_element = soup.find("main")
                if not main_element:
                    logging.error("Could not find main element in response html.")
                    raise ExchangeRateFetchError(
                        "Could not find main element in response html."
                    )

                digits_span = soup.find("span", class_="faded-digits")

                if digits_span is None:
                    logging.critical("Could not find digits span in response html.")
                    return -1

                digits_str: str = digits_span.get_text()
                parent_div = digits_span.parent  # type:ignore

                # Get first element of the iterator
                for child in parent_div.children:  # type:ignore
                    rate_p = str(child)
                    break

                amount_of_zero = len(rate_p.split(".")[-1])
                digits_to_sum = ("0." + ("0" * amount_of_zero)) + digits_str
                rate = float(rate_p) + float(digits_to_sum)
                logging.info("Retrieved exchange rate: " + str(rate))
                return rate

            except TimeoutException as e:
                msg = f"The request timed out fetching the exchange rate for {currency.upper()}.\n{traceback.format_exc()}"
                logging.critical(msg)
                raise ExchangeRateFetchError(msg) from e

            except NetworkError as e:
                msg = f"A network error has ocurred trying to fetch the exchange rate for {currency.upper()}.\nPlease check your internet connection."
                logging.critical(msg)
                raise ExchangeRateFetchError(msg) from e

            except HTTPStatusError as e:
                msg = f"Server responded with an error when fetching exchange rate for {currency.upper()}.\n{traceback.format_exc()}"
                logging.critical(msg)
                raise ExchangeRateFetchError(msg) from e
            except Exception as e:
                msg = f"An unkown error has ocurred trying to fetch the exchange rate for {currency.upper()}.\n{traceback.format_exc()}"
                logging.critical(msg)
                raise ExchangeRateFetchError(msg) from e

    def _get_all_local_rates(self) -> dict[str, dict[str, RatesData]]:
        """
        Retrieves the exchange rates from a local file.

        Returns:
            dict: The exchange rates.
        """
        if not os.path.exists(self.file_path):
            return {}

        with open(self.file_path, "r", encoding="UTF-8") as f:
            rates: dict[str, dict[str, RatesData]] = json.load(f)

        return rates

    def _save_exchange(
        self, base_currency: str, currency: str, exchange: float
    ) -> None:
        """
        Saves the exchange rate between the base currency and the given currency to disk.

        Args:
            base_currency (str): The base currency.
            currency (str): The currency to convert to.
            exchange (float): The exchange rate.
        """

        logging.info(
            f"Saving exchange rate for {base_currency}-{currency} at {exchange}..."
        )
        logging.info("Retrieving local rates to save...")
        CurrencyManager.CURRENT_RATES = self._get_all_local_rates()
        logging.debug(f"Current rates: {CurrencyManager.CURRENT_RATES}")

        # In case the rates file is not created.
        if not CurrencyManager.CURRENT_RATES:
            CurrencyManager.CURRENT_RATES = {
                base_currency: {
                    currency: {
                        "retrieve_timestamp": round(Arrow.now().timestamp()),
                        "rate": exchange,
                    }
                }
            }

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(CurrencyManager.CURRENT_RATES, f, indent=4)

            return

        if base_currency not in CurrencyManager.CURRENT_RATES:
            CurrencyManager.CURRENT_RATES[base_currency] = {}

        CurrencyManager.CURRENT_RATES[base_currency][currency] = {
            "retrieve_timestamp": round(Arrow.now().timestamp()),
            "rate": exchange,
        }

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(CurrencyManager.CURRENT_RATES, f, indent=4)

        logging.info("Exchange rate saved successfully.")
