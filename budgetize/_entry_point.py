"""Entry point when running budgetize cmd"""

from budgetize.tui import TuiApp


def main() -> None:
    """Runs Budgetize"""
    TuiApp().run()
