"""Entry point when running budgetize cmd"""

from budgetize.tui import TuiApp


def run() -> None:
    """Runs Budgetize"""
    TuiApp().run()
