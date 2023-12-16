import os
from pathlib import Path
from user import User
import json


def load_user_data() -> User:
    """Loads all the user data from the data file."""

    data_path = Path(os.path.expanduser("~"), ".pyfinance", "finances.bin")
    with open(data_path, "r") as f:
        data = json.load(f)

        return User.from_file_data(data)


def write_user_data(user: User) -> None:
    """Writes the user data to the data file."""

    data_path = Path(os.path.expanduser("~"), ".pyfinance", "finances.bin")
    with open(data_path, "w") as f:
        f.write(json.dumps(user.get_data_file_content()))
