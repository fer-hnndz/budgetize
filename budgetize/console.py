"""Entry point when running budgetize cmd"""

import logging
import os

from budgetize.consts import APP_FOLDER_PATH
from budgetize.tui import TuiApp


def run() -> None:
    """Runs Budgetize"""

    log_path = os.path.join(APP_FOLDER_PATH, "budgetize.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s ] (%(module)s.%(funcName)s | %(levelname)s) %(message)s",
        datefmt="%d/%m/%Y @ %H:%M:%S %Z",
        filename=log_path,
    )

    TuiApp().run()
