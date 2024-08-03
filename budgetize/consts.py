"Module that stores constant variables for the app such like names or paths"

import os

import pkg_resources
from babel import Locale

VERSION = "0.2.1"
VALID_EXCHANGE_TIMESTAMP = 7 * 24 * 60 * 60  # 1 week in seconds
# Database

APP_FOLDER_NAME = ".budgetize"

user_folder = os.path.expanduser("~")
APP_FOLDER_PATH = os.path.join(user_folder, ".budgetize")
DB_FILE_NAME = "budgetize.sqlite"
EXPORT_DATA_EXTENSION = "bdgz"
PROD_DB_URL = f"sqlite:///{os.path.join(APP_FOLDER_PATH, DB_FILE_NAME)}"
BACKUPS_FOLDER = os.path.join(APP_FOLDER_PATH, "backups")

# Localization
TRANSLATIONS_PATH: str = pkg_resources.resource_filename("budgetize", "translations")

if not os.path.exists(APP_FOLDER_PATH):
    os.makedirs(APP_FOLDER_PATH)


# Dummy definition for Babel to extract the strings
def _(msg: str) -> str:
    return msg


DEFAULT_CATEGORIES = [
    _("Income"),
    _("Food"),
    _("Groceries"),
    _("Medicine"),
    _("Car"),
    _("Gifts"),
    _("Investment"),
    _("Entertainment"),
]

del _

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
    "language": "",
    "categories": DEFAULT_CATEGORIES,
    "base_currency": "",
}

RICH_COLORS = [
    "green3",
    "cyan1",
    "blue_violet",
    "cornflower_blue",
    "medium_violet_red",
    "orange3",
    "yellow1",
    "dodger_blue",
    "dark_olive_green1",
]

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
