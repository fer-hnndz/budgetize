"Module that stores constant variables for the app such like names or paths"

import os

import pkg_resources
from babel import Locale

# ExchangeRates API

EXCHANGERATES_FREE_API_KEY = "9c21e1d06665202b12fb2962b75c4e35"
VALID_EXCHANGE_TIMESTAMP = 36 * 60  # 36 hours

# Database

APP_FOLDER_NAME = ".budgetize"

user_folder = os.path.expanduser("~")
APP_FOLDER_PATH = os.path.join(user_folder, ".budgetize")
DB_FILE_NAME = "budgetize.sqlite"
PROD_DB_URL = f"sqlite:///{os.path.join(APP_FOLDER_PATH, DB_FILE_NAME)}"

# Localization
TRANSLATIONS_PATH = pkg_resources.resource_filename("budgetize", "translations")
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

AVAILABLE_LANGUAGES: list[tuple[str, str]] = [
    (Locale("en").display_name, "en"),
]

locale_dirs = os.listdir(TRANSLATIONS_PATH)
for locale_dir in locale_dirs:
    if os.path.isdir(os.path.join(TRANSLATIONS_PATH, locale_dir)):
        AVAILABLE_LANGUAGES.append(
            (Locale(locale_dir).display_name.title(), locale_dir)
        )

# Settings
DEFAULT_SETTINGS = {
    "language": "en",
    "categories": DEFAULT_CATEGORIES,
    "base_currency": "",
}


CURRENCIES: list[tuple[str, str]] = [
    ("SHP", "St. Helena Pound"),
    ("EUR", "Euro"),
    ("AED", "درهم إماراتي"),
    ("AFN", "افغانی افغانستان"),
    ("XCD", "East Caribbean Dollar"),
    ("ALL", "Leku Shqiptar"),
    ("AMD", "Հայկական Դրամ"),
    ("AOA", "Kwanza Angolano"),
    ("ARS", "Peso Argentino"),
    ("USD", "US Dollar"),
    ("AUD", "Australian Dollar"),
    ("AWG", "Arubaanse Gulden"),
    ("ANG", "Nederlands-Antilliaanse Gulden"),
    ("AZN", "Azərbaycan Manati"),
    ("BAM", "Конвертибилна Марка"),
    ("BBD", "Barbadian Dollar"),
    ("BDT", "বাংলাদেশী টাকা"),
    ("PKR", "পাকিস্তানি রুপি"),
    ("INR", "ভারতীয় রুপি"),
    ("XOF", "Franc Cfa (Bceao)"),
    ("BGN", "Български Лев"),
    ("BHD", "دينار بحريني"),
    ("BIF", "Ifaranga Ry'Uburundi"),
    ("BMD", "Bermudan Dollar"),
    ("BND", "Dolar Brunei"),
    ("MYR", "Ringgit Malaysia"),
    ("BOB", "Boliviano"),
    ("BRL", "Real Brasileiro"),
    ("BSD", "Bahamian Dollar"),
    ("BTN", "དངུལ་ཀྲམ"),
    ("NOK", "Norwegian Krone"),
    ("BWP", "Botswanan Pula"),
    ("ZAR", "South African Rand"),
    ("BYN", "Беларускі Рубель"),
    ("BZD", "Belize Dollar"),
    ("CAD", "Canadian Dollar"),
    ("CDF", "Franc Congolais"),
    ("XAF", "Farânga Cfa (Beac)"),
    ("CHF", "Schweizer Franken"),
    ("NZD", "New Zealand Dollar"),
    ("CLP", "Peso Chileno"),
    ("CNY", "人民币"),
    ("COP", "Peso Colombiano"),
    ("CRC", "Colón Costarricense"),
    ("CUP", "Peso Cubano"),
    ("CVE", "Escudo Cabo-Verdiano"),
    ("CZK", "Česká Koruna"),
    ("DKK", "Dansk Krone"),
    ("DOP", "Peso Dominicano"),
    ("DZD", "دينار جزائري"),
    ("EGP", "جنيه مصري"),
    ("ETB", "Ethiopian Birr"),
    ("FIM", "Suomen Markka"),
    ("FJD", "Fijian Dollar"),
    ("FKP", "Falkland Islands Pound"),
    ("GBP", "British Pound"),
    ("GEL", "ქართული ლარი"),
    ("GHS", "Ghanaian Cedi"),
    ("GIP", "Gibraltar Pound"),
    ("GMD", "Gambian Dalasi"),
    ("GNF", "Franc Guinéen"),
    ("GNS", "Syli Guinéen"),
    ("GTQ", "Quetzal Guatemalteco"),
    ("GYD", "Guyanaese Dollar"),
    ("HKD", "港幣"),
    ("HNL", "Lempira Hondureño"),
    ("HRK", "Hrvatska Kuna"),
    ("HTG", "Haitian Gourde"),
    ("HUF", "Magyar Forint"),
    ("IDR", "Rupiah Indonesia"),
    ("ILS", "שקל חדש"),
    ("IQD", "دينار عراقي"),
    ("IRR", "ریال ایران"),
    ("ISK", "Íslensk Króna"),
    ("JMD", "Jamaican Dollar"),
    ("JOD", "دينار أردني"),
    ("KES", "Shilingi Ya Kenya"),
    ("KGS", "Кыргызстан Сому"),
    ("KHR", "រៀល\u200bកម្ពុជា"),
    ("KMF", "فرنك جزر القمر"),
    ("KPW", "조선 민주주의 인민 공화국 원"),
    ("KRW", "대한민국 원"),
    ("KWD", "دينار كويتي"),
    ("KYD", "Cayman Islands Dollar"),
    ("KZT", "Казахский Тенге"),
    ("LAK", "ລາວ ກີບ"),
    ("LBP", "جنيه لبناني"),
    ("LKR", "ශ්\u200dරී ලංකා රුපියල"),
    ("LRD", "Liberian Dollar"),
    ("LSL", "Lsl"),
    ("LTL", "Lietuvos Litas"),
    ("LVL", "Latvijas Lats"),
    ("LYD", "دينار ليبي"),
    ("MAD", "درهم مغربي"),
    ("MDL", "Leu Moldovenesc"),
    ("MGA", "Ariary"),
    ("MKD", "Македонски Денар"),
    ("MMK", "မြန်မာ ကျပ်"),
    ("MNT", "Монгол Төгрөг"),
    ("MOP", "澳門元"),
    ("MRU", "أوقية موريتانية"),
    ("MUR", "Mauritian Rupee"),
    ("MVR", "Mvr"),
    ("MWK", "Malawian Kwacha"),
    ("MXN", "Peso Mexicano"),
    ("MZN", "Metical Moçambicano"),
    ("NAD", "Namibian Dollar"),
    ("NGN", "Nigerian Naira"),
    ("NIO", "Córdoba Oro"),
    ("NPR", "नेपाली रूपैयाँ"),
    ("OMR", "ريال عماني"),
    ("PAB", "Balboa Panameño"),
    ("PEN", "Sol Peruano"),
    ("PGK", "Pgk"),
    ("PHP", "Philippine Peso"),
    ("PLN", "Złoty Polski"),
    ("PYG", "Pyg"),
    ("QAR", "ريال قطري"),
    ("RON", "Leu Românesc"),
    ("RSD", "Srpski Dinar"),
    ("RUB", "Российский Рубль"),
    ("RWF", "Rwf"),
    ("SAR", "ريال سعودي"),
    ("SBD", "Solomon Islands Dollar"),
    ("SCR", "Roupie Des Seychelles"),
    ("SDG", "Sudanese Pound"),
    ("SEK", "Svenske Kroner"),
    ("SGD", "Singapore Dollar"),
    ("SIT", "Slovenski Tolar"),
    ("SKK", "Slovenská Koruna"),
    ("SLL", "Sierra Leonean Leone (1964—2022)"),
    ("SOS", "Shilingka Soomaaliya"),
    ("SRD", "Surinaamse Dollar"),
    ("STN", "Dobra De São Tomé E Príncipe"),
    ("SYP", "ليرة سورية"),
    ("SZL", "Swazi Lilangeni"),
    ("THB", "บาท"),
    ("TJS", "Сомонӣ"),
    ("TMT", "Türkmen Manady"),
    ("TND", "دينار تونسي"),
    ("TOP", "Pa'Anga Fakatonga"),
    ("TRY", "Türk Liras"),
    ("TTD", "Trinidad & Tobago Dollar"),
    ("TWD", "新台幣"),
    ("TZS", "Shilingi Ya Tanzania"),
    ("UAH", "Українська Гривня"),
    ("UGX", "Shilingi Ya Uganda"),
    ("UYU", "Peso Uruguayo"),
    ("UZS", "O'Zbekiston So'Mi"),
    ("VES", "Bolívar Venezolano"),
    ("VND", "Đồng Việt Nam"),
    ("VUV", "Vanuatu Vatu"),
    ("WST", "Samoan Tala"),
    ("YER", "ريال يمني"),
    ("ZAR", "South African Rand"),
    ("ZMW", "Zambian Kwacha"),
]
