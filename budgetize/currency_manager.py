"""Module that handles requests to the currency exchanges API"""

import json
import logging
import os
import traceback
from typing import Optional

import httpx
from arrow import Arrow
from bs4 import BeautifulSoup
from httpx import HTTPStatusError, NetworkError, TimeoutException

from budgetize.consts import APP_FOLDER_PATH
from budgetize.exceptions import ExchangeRateFetchError
from budgetize.exchange_rate import ExchangeRate

logger = logging.getLogger(__name__)


class CurrencyManager:
    """
    Class that handles requests to the currency exchanges API and saves it to disk.

    Format of the CURRENT_RATES dict:
        "main_currency": {
            "currency": ExchangeRate
        }

    Example
    "USD": {
        "EUR": ExchangeRate<"EUR", 0.85, 0>
    }

    Parameters
    ----------
    base_currency : str
        The base currency to convert from.
    """

    CURRENT_RATES: dict[str, dict[str, ExchangeRate]] = {}

    def __init__(self, base_currency: str):
        self.file_path = os.path.join(APP_FOLDER_PATH, "currency_exchanges.json")
        self.base_currency = base_currency

        self._update_rates_from_disk()

    # ============== PUBLIC METHODS ==============

    async def get_exchange(self, currency: str) -> float:
        """(Coroutine) Retrieves the exchange rate between the base currency and the given currency.

        Attempts to get it from the disk to avoid fetching it from the internet, but if the exchange is not valid, it
        is updated from the internet.

        Args:
        ----
            currency (str): The currency to convert to.

        Returns:
        -------
            float: The exchange rate.
        """

        logger.info(
            "Retrieving exchange rate for {}-{}...".format(self.base_currency, currency)
        )

        if self.base_currency not in CurrencyManager.CURRENT_RATES:
            return await self.fetch_and_save_rate(currency)

        if currency not in CurrencyManager.CURRENT_RATES[self.base_currency]:
            return await self.fetch_and_save_rate(currency)

        return CurrencyManager.CURRENT_RATES[self.base_currency][currency].rate

    async def update_invalid_rates(self) -> bool:
        """(Coroutine) Updates all the rates that have expired. Returns True if successful."""

        if not self.has_expired_rates():
            logger.info("No rates have expired. Skipping...")
            return True

        logger.warning("Some rates have expired. Updating...")

        for currency, exchange in CurrencyManager.CURRENT_RATES[
            self.base_currency
        ].items():
            if not exchange.is_expired():
                continue

            logger.info(
                "Rate for {}-{} has expired. Updating...".format(
                    self.base_currency, currency
                )
            )
            rate = await self.fetch_and_save_rate(currency)
            logger.info("Saving fetched exchange rate...")
            self._save_exchange(currency, rate)

        return True

    def has_expired_rates(self) -> bool:
        """Returns True if there is a rate that has expired."""

        logger.info("Checking for invalid rates...")
        self._update_rates_from_disk()
        if not CurrencyManager.CURRENT_RATES:
            return False

        if self.base_currency not in CurrencyManager.CURRENT_RATES.values():
            return True

        for _, data in CurrencyManager.CURRENT_RATES[self.base_currency].items():
            if data.is_expired():
                return True
        return False

    # =============== Exchange Rate Internet-Based Fetch Methods ===============

    async def fetch_and_save_rate(self, currency: str) -> float:
        """
        (Coroutine) Fetches the currency exchange rate between the base currency and the given currency.
        Rate is then saved to the local disk.

        Args
        ----
            currency (str): The currency to convert to.

        Returns
        -------
            float: The exchange rate retrieved. Returns -1 if an error ocurred.
        """

        exchange = await self._retrieve_exchange_rate(currency)
        if exchange < 0:
            return -1
        self._save_exchange(currency, exchange)
        return exchange

    async def _retrieve_exchange_rate(self, currency: str) -> float:
        """(Coroutine) Retrieves from the internet the exchange rate between the base currency and the given currency.

        Args:
        ----
            currency (str): The currency to convert to.

        Returns:
        -------
            float: The exchange rate.

        Raises
        ------
            ExchangeRateFetchError: If an error ocurred while fetching the exchange rate.


        """
        async with httpx.AsyncClient() as client:
            url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={self.base_currency.upper()}&To={currency.upper()}"
            logger.info("Attempting to fetch exchange rate at {}".format(url))
            try:
                r = await client.get(url, timeout=8)
                logger.debug("Response status code: {}".format(r.status_code))
                logger.info("Saving response HMTL...")
                self._save_last_html_response(r.text)

                soup = BeautifulSoup(r.text, "html.parser")

                main_element = soup.find("main")
                if not main_element:
                    logger.error("Could not find main element in response html.")
                    raise ExchangeRateFetchError(
                        "Could not find main element in response html."
                    )

                digits_span = soup.find("span", class_="faded-digits")

                if digits_span is None:
                    logger.critical("Could not find digits span in response html.")
                    raise ExchangeRateFetchError(
                        "Could not scrape exchange rate. Please look at last_html_response.html in Budgetize's folder"
                    )

                digits_str: str = digits_span.get_text().replace(",", "")
                logger.debug("Faded Digits from SPAN: {}".format(digits_str))
                parent_div = digits_span.parent  # type:ignore

                # Get first element of the iterator
                for child in parent_div.children:  # type:ignore
                    rate_p = str(child).replace(",", "")
                    break

                amount_of_zero = len(rate_p.split(".")[-1])
                digits_to_sum = ("0." + ("0" * amount_of_zero)) + digits_str
                rate = float(rate_p) + float(digits_to_sum)
                logger.info("Retrieved exchange rate: {}".format(rate))
                return rate

            except TimeoutException as e:
                msg = "The request timed out fetching the exchange rate for {}.\n{}".format(
                    currency.upper(), traceback.format_exc()
                )
                logger.critical(msg)
                raise ExchangeRateFetchError(msg) from e

            except NetworkError as e:
                msg = "A network error has ocurred trying to fetch the exchange rate for {}.\nPlease check your internet connection.".format(
                    currency.upper()
                )
                logger.critical(msg)
                raise ExchangeRateFetchError(msg) from e

            except HTTPStatusError as e:
                msg = "Server responded with an error when fetching exchange rate for {}.\n{}".format(
                    currency.upper(), traceback.format_exc()
                )
                logger.critical(msg)
                raise ExchangeRateFetchError(msg) from e
            except Exception as e:
                msg = "An unkown error has ocurred trying to fetch the exchange rate for {}.\n{}".format(
                    currency.upper(), traceback.format_exc()
                )
                logger.critical(msg)
                raise ExchangeRateFetchError(msg) from e

    def _save_last_html_response(self, response: str) -> None:
        """Saves last HTML in a file"""
        path = os.path.join(APP_FOLDER_PATH, "last_html_response.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(response)

    # ==================== Disk Operation Methods ====================

    def _save_exchange(
        self,
        currency: str,
        exchange: float,
    ) -> None:
        """Saves the exchange rate between the base currency and the given currency to disk.

        Args:
        ----
            base_currency (str): The base currency.
            currency (str): The currency to convert to.
            exchange (float): The exchange rate.

        """
        logger.info(
            "Saving exchange rate for {}-{} at {}...".format(
                self.base_currency, currency, exchange
            )
        )
        logger.debug("Current rates: {}".format(CurrencyManager.CURRENT_RATES))
        exchange_obj = ExchangeRate(
            currency=currency,
            rate=exchange,
            retrieve_timestamp=round(Arrow.now().timestamp()),
        )

        if not CurrencyManager.CURRENT_RATES:
            CurrencyManager.CURRENT_RATES = {
                self.base_currency: {currency: exchange_obj},
            }

        if self.base_currency not in CurrencyManager.CURRENT_RATES:
            CurrencyManager.CURRENT_RATES[self.base_currency] = {currency: exchange_obj}
        else:
            CurrencyManager.CURRENT_RATES[self.base_currency][currency] = exchange_obj

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.__current_rates_to_json(), f, indent=4)

        logger.info("Exchange rate saved successfully.")

    def get_exchange_from_disk(self, currency: str) -> Optional[ExchangeRate]:
        """Retrieves the exchange rate between the base currency and the given currency from disk.
        NOTE: No checks for outdated rates are made.

        Args:
        ----
            currency (str): The currency to convert to.

        Returns:
        -------
            float: The exchange rate.

        """

        logger.info("Retrieving exchange rate from disk...")
        self._update_rates_from_disk()

        if not CurrencyManager.CURRENT_RATES:
            return None

        if self.base_currency not in CurrencyManager.CURRENT_RATES:
            return None

        return CurrencyManager.CURRENT_RATES[self.base_currency].get(currency, None)

    def __current_rates_to_json(self) -> dict:
        """Converts the CURRENT_RATES dict to a valid json.

        Returns
        -------
            dict: The CURRENT_RATES dict.

        """

        json_dict: dict[str, dict] = {}

        for base_currency, _ in CurrencyManager.CURRENT_RATES.items():
            json_dict[base_currency] = {}

            for currency, data in CurrencyManager.CURRENT_RATES[base_currency].items():
                json_dict[base_currency][currency] = data.to_dict()

        return json_dict

    def _update_rates_from_disk(self) -> None:
        """Updates the exchange rates from a local file.

        Returns
        -------
            dict: The exchange rates.

        """

        if not os.path.exists(self.file_path):
            return

        with open(self.file_path, encoding="UTF-8") as f:
            rates: dict[str, dict[str, dict]] = json.load(f)

            # Convert the rates to ExchangeRate objects
            for base_currency, currencies in rates.items():
                CurrencyManager.CURRENT_RATES[base_currency] = {}

                for currency, data in currencies.items():
                    CurrencyManager.CURRENT_RATES[base_currency][
                        currency
                    ] = ExchangeRate.from_dict(data)
