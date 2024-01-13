"""
Util functions for the CLI
"""

import json
import os

import core.consts as consts
from core.user import User


def should_run_initial_config() -> bool:
    """
    Returns if the app should run the initial config for creating a user
    """

    # Make sure if we need to run initial config

    # Check the user folder and if it contains the app folder
    data_path = os.path.join(os.path.expanduser("~"), consts.APP_FOLDER_NAME)

    # If the folder does not exist, run initial config
    if not os.path.exists(data_path):
        return True

    # Check if the folder has the user file, if it does not exist, run the config
    if not consts.USER_FILE_NAME in os.listdir(data_path):
        return True

    # Check that the json file is readable
    try:
        user = load_user_data()
        return False
    except:
        return True


def load_user_data() -> User:
    """Loads all the user data from the data file."""

    data_path = os.path.join(
        os.path.expanduser("~"), consts.APP_FOLDER_NAME, consts.USER_FILE_NAME
    )
    with open(data_path) as f:
        data = json.load(f)
        return User.from_file_data(data)


def save_user_data(user: User):
    data_folder = os.path.join(os.path.expanduser("~"), consts.APP_FOLDER_NAME)

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    data_path = os.path.join(data_folder, consts.USER_FILE_NAME)
    with open(data_path, "w") as f:
        f.write(json.dumps(user.to_dict(), indent=4))
