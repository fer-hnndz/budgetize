"""Util functions for Budgetize"""

import gettext
import logging
import os

from budgetize import SettingsManager
from budgetize.consts import APP_FOLDER_PATH, CURRENCIES, TRANSLATIONS_PATH


def create_logger() -> None:
    """Creates the app Logger"""

    log_path = os.path.join(APP_FOLDER_PATH, f"budgetize.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s UTC] (%(module)s.%(funcName)s | %(levelname)s) %(message)s",
        datefmt="%d/%m/%Y @ %H:%M:%S",
        filename=log_path,
    )


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
