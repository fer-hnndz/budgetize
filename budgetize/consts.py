"Module that stores constant variables for the app such like names or paths"

import os

# ExchangeRates API

EXCHANGERATES_FREE_API_KEY = "9c21e1d06665202b12fb2962b75c4e35"
VALID_EXCHANGE_TIMESTAMP = 36 * 60  # 36 hours

# Database

APP_FOLDER_NAME = ".budgetize"

user_folder = os.path.expanduser("~")
app_folder_path = os.path.join(user_folder, ".budgetize")
if not os.path.exists(app_folder_path):
    os.mkdir(app_folder_path)

DB_FILE_NAME = "budgetize.sqlite"
PROD_DB_URL = f"sqlite:///{os.path.join(app_folder_path, DB_FILE_NAME)}"

DEFAULT_CATEGORIES = [
    "Income",
    "Food",
    "Groceries",
    "Medicine",
    "Car",
    "Gifts",
    "Investment",
    "Entertainment",
]

# Settings
DEFAULT_SETTINGS = {
    "language": "en",
}


CURRENCIES: list[tuple[str, str]] = [
    ("AED", "United Arab Emirates Dirham"),
    ("AFN", "Afghan Afghani"),
    ("ALL", "Albanian Lek"),
    ("AMD", "Armenian Dram"),
    ("ANG", "Netherlands Antillean Guilder"),
    ("AOA", "Angolan Kwanza"),
    ("ARS", "Argentine Peso"),
    ("AUD", "Australian Dollar"),
    ("AWG", "Aruban Florin"),
    ("AZN", "Azerbaijani Manat"),
    ("BAM", "Bosnia-Herzegovina Convertible Mark"),
    ("BBD", "Barbadian Dollar"),
    ("BDT", "Bangladeshi Taka"),
    ("BGN", "Bulgarian Lev"),
    ("BHD", "Bahraini Dinar"),
    ("BIF", "Burundian Franc"),
    ("BMD", "Bermudian Dollar"),
    ("BND", "Brunei Dollar"),
    ("BOB", "Bolivian Boliviano"),
    ("BRL", "Brazilian Real"),
    ("BSD", "Bahamian Dollar"),
    ("BTC", "Bitcoin"),
    ("BTN", "Bhutanese Ngultrum"),
    ("BWP", "Botswana Pula"),
    ("BYN", "Belarusian Ruble"),
    ("BYR", "Belarusian Ruble (pre-2016)"),
    ("BZD", "Belize Dollar"),
    ("CAD", "Canadian Dollar"),
    ("CDF", "Congolese Franc"),
    ("CHF", "Swiss Franc"),
    ("CLF", "Chilean Unit of Account (UF)"),
    ("CLP", "Chilean Peso"),
    ("CNY", "Chinese Yuan"),
    ("COP", "Colombian Peso"),
    ("CRC", "Costa Rican Colón"),
    ("CUC", "Cuban Convertible Peso"),
    ("CUP", "Cuban Peso"),
    ("CVE", "Cape Verdean Escudo"),
    ("CZK", "Czech Koruna"),
    ("DJF", "Djiboutian Franc"),
    ("DKK", "Danish Krone"),
    ("DOP", "Dominican Peso"),
    ("DZD", "Algerian Dinar"),
    ("EGP", "Egyptian Pound"),
    ("ERN", "Eritrean Nakfa"),
    ("ETB", "Ethiopian Birr"),
    ("EUR", "Euro"),
    ("FJD", "Fijian Dollar"),
    ("FKP", "Falkland Islands Pound"),
    ("GBP", "British Pound Sterling"),
    ("GEL", "Georgian Lari"),
    ("GGP", "Guernsey Pound"),
    ("GHS", "Ghanaian Cedi"),
    ("GIP", "Gibraltar Pound"),
    ("GMD", "Gambian Dalasi"),
    ("GNF", "Guinean Franc"),
    ("GTQ", "Guatemalan Quetzal"),
    ("GYD", "Guyanaese Dollar"),
    ("HKD", "Hong Kong Dollar"),
    ("HNL", "Honduran Lempira"),
    ("HRK", "Croatian Kuna"),
    ("HTG", "Haitian Gourde"),
    ("HUF", "Hungarian Forint"),
    ("IDR", "Indonesian Rupiah"),
    ("ILS", "Israeli New Shekel"),
    ("IMP", "Isle of Man Pound"),
    ("INR", "Indian Rupee"),
    ("IQD", "Iraqi Dinar"),
    ("IRR", "Iranian Rial"),
    ("ISK", "Icelandic Króna"),
    ("JEP", "Jersey Pound"),
    ("JMD", "Jamaican Dollar"),
    ("JOD", "Jordan"),
]
