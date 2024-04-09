"""This is the file that should be run in development to start Budgetize."""

from budgetize.tui import TuiApp

if __name__ == "__main__":
    # To run budgetize from PyPi installation, use `budgetize` command.
    TuiApp().run()
