"""Util functions for Budgetize"""

import gettext

from budgetize import SettingsManager
from budgetize.consts import CURRENCIES, TRANSLATIONS_PATH

_t = gettext.translation(
    "budgetize",
    TRANSLATIONS_PATH,
    languages=[SettingsManager().get_language()],
    fallback=True,
)

# Definition of the translating function
_ = _t.gettext


def get_select_currencies() -> list[tuple[str, str]]:
    """Returns available currencies for the Select widget.
    ( (SYMBOL) Name, symbol )
    """

    res = []
    for curr in CURRENCIES:
        res.append((f"({curr[0]}) {curr[1]}", curr[0]))

    res.sort()
    return res


# This array is to help Babel extract these default categories.
LOCALIZED_CATEGORIES = [
    _("Income"),
    _("Food"),
    _("Groceries"),
    _("Medicine"),
    _("Car"),
    _("Gifts"),
    _("Investment"),
    _("Entertainment"),
]
