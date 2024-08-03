import logging
import os

"""This is the file that should be run in development to start Budgetize."""

from budgetize.consts import APP_FOLDER_PATH
from budgetize.tui import TuiApp

if __name__ == "__main__":

    log_path = os.path.join(APP_FOLDER_PATH, "budgetize.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s ] (%(module)s.%(funcName)s | %(levelname)s) %(message)s",
        datefmt="%d/%m/%Y @ %H:%M:%S %Z",
        filename=log_path,
    )

    # To run budgetize from PyPi installation, use `budgetize` command.
    TuiApp().run()
