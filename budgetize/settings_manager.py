"""Module that defines the settings manager class which manages user's settings"""

import json
import os
from pathlib import Path
from typing import TypedDict

from babel import Locale

from budgetize.consts import APP_FOLDER_PATH, DEFAULT_SETTINGS


class SettingsDict(TypedDict):
    """Dict that represents the settings json"""

    language: str
    categories: list[str]
    base_currency: str


class SettingsManager:
    """Manager for user's settings."""

    def __init__(self) -> None:
        """
        Create a new manager for user's settings.

        This class is the only one that should modify any of the user's settings.
        """

        self._app_folder_path = Path(APP_FOLDER_PATH)
        self._settings_path = self._app_folder_path.joinpath("settings.json")

        #! Make this a class variable so it is shared between all instances and avoid constant reloading?
        self._settings: SettingsDict = {}  # type: ignore
        self._reload_settings()

    def _reload_settings(self) -> None:
        """Reloads user settings from disk."""
        if not self._settings_exist():
            self._create_default_settings()

        with open(
            self._app_folder_path.joinpath("settings.json"), encoding="utf-8"
        ) as f:
            self._settings = json.load(f)

    def _settings_exist(self) -> bool:
        """Checks if the settings file exists."""
        return self._settings_path.exists()

    def _create_default_settings(self) -> None:
        """Creates the default settings file."""
        if not Path(APP_FOLDER_PATH).exists():
            os.mkdir(APP_FOLDER_PATH)

        with open(self._settings_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)

    def is_default_settings(self) -> bool:
        """Returns True if user has default settings (no lang or currency)."""
        return not self.get_language() and not self.get_base_currency()

    def get_language(self) -> str:
        """Returns the user's language code for the app."""
        self._reload_settings()
        return self._settings["language"]

    def get_locale(self) -> Locale:
        """Returns a Locale object based from the user's selected language."""
        self._reload_settings()
        return Locale(self._settings["language"])

    def get_base_currency(self) -> str:
        """Returns the user's selected currency."""
        self._reload_settings()
        return self._settings["base_currency"]

    def get_categories(self) -> list[str]:
        """Returns the user's selected categories."""
        self._reload_settings()
        return self._settings["categories"]

    def set_categories(self, categories: list[str]) -> None:
        """Sets the user's categories and saves them."""
        self._settings["categories"] = categories
        self.save(self._settings)

    def save(self, settings: SettingsDict) -> None:
        """Saves the user's settings."""
        self._settings = settings
        with open(self._settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
