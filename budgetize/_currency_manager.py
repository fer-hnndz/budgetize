"Module that handles requests to the currency exchanges API"
import json
import os

import requests
from arrow import Arrow

from budgetize import consts


# TODO: Improve this class so it is more user-friendly
class CurrencyManager:
    """Class that handles requests to the currency exchanges API and saves it to disk"""

    def __init__(self, base_currency: str):
        """
        Creates a new CurrencyManager object.
        By default, it uses a free API key from https://exchangeratesapi.io/.

        If you wish to use a different API key,
        create a new file called "exchangeratesapi.txt" in `.budgetize` folder
        located in your user folder.
        """

        self.base_currency = base_currency
        self.key = self._get_api_key()

    def _get_api_key(self):
        app_folder = os.path.join(os.path.expanduser("~"), ".budgetize")
        api_key_file = os.path.join(app_folder, "exchangeratesapi.txt")

        if not os.path.exists(api_key_file):
            return consts.EXCHANGERATES_FREE_API_KEY

        with open(api_key_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _retrieve_exchange_rates(self) -> bool:
        """
        Retrieves exchange rates from the API
        and saves it to exchange_rates.json file.

        Returns `True` if request was successful.
        """

        base_url: str = (
            f"http://api.exchangeratesapi.io/v1/latest?access_key={self.key}"
        )
        headers = {"Content-Type": "application/json"}
        print("Requesting with url: " + base_url)

        response = requests.get(base_url, headers=headers, timeout=5)
        print(response.text)

        if response.status_code != 200:
            return False

        data = response.json()
        with open("exchange_rates.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return True

    def get_all_exchanges(self) -> dict:
        """
        Gets all exchange rates.
        If the data is older than the constant `VALID_EXCHANGE_TIMESTAMP`,
        it will retrieve new data.
        """

        # Check if exchange file exists
        app_folder = os.path.join(os.path.expanduser("~"), ".budgetize")

        exchange_file = os.path.join(
            os.path.expanduser("~"), ".budgetize", "exchange_rates.json"
        )

        if not os.path.exists(app_folder):
            os.mkdir(app_folder)

        # Retrive data
        if os.path.exists(exchange_file):
            data = None

            with open("exchange_rates.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            last_retrieved_timestamp = data["timestamp"]

            # If the data is older than 36 hours, retrieve new data
            if (
                Arrow.now().timestamp - last_retrieved_timestamp
                > consts.VALID_EXCHANGE_TIMESTAMP
            ):
                self._retrieve_exchange_rates()
        else:  # If file does not exist, retrive new data
            self._retrieve_exchange_rates()

        # Load data

        file_data = None
        with open("exchange_rates.json", "r", encoding="utf-8") as f:
            file_data = json.load(f)

        return file_data["rates"]
