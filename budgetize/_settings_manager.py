import json
import os
from pathlib import Path
from typing import TypedDict

from babel import Locale

from budgetize.consts import APP_FOLDER_PATH, DEFAULT_SETTINGS


class SettingsDict(TypedDict):
    language: str
    default_categories: list[str]
    base_currency: str


class SettingsManager:
    def __init__(self) -> None:
        """Create a new manager for user's settings.
        This class is the only one that should modify any of the user's settings.
        """

        self.app_folder_path = Path(APP_FOLDER_PATH)
        self.settings_path = self.app_folder_path.joinpath("settings.json")

        if not self._settings_exist():
            self._create_default_settings()

        self.settings: SettingsDict = {}  # type: ignore
        with open(
            self.app_folder_path.joinpath("settings.json"), encoding="utf-8"
        ) as f:
            self.settings = json.load(f)

    def _settings_exist(self) -> bool:
        """Checks if the settings file exists"""

        return self.settings_path.exists()

    def _create_default_settings(self) -> None:
        """Creates the default settings file."""

        if not Path(APP_FOLDER_PATH).exists():
            os.mkdir(APP_FOLDER_PATH)

        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)

    def get_language(self) -> str:
        """Returns the user's language code for the app."""
        return self.settings["language"]

    def get_locale(self) -> Locale:
        """Returns a Locale object based from the user's selected language."""
        return Locale(self.settings["language"])
