"""Util functions for Budgetize"""

import gettext

from budgetize import SettingsManager
from budgetize.consts import TRANSLATIONS_PATH

_t = gettext.translation(
    "budgetize",
    TRANSLATIONS_PATH,
    languages=[SettingsManager().get_language()],
    fallback=True,
)

# Definition of the translating function
_ = _t.gettext
