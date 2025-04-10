import os
import json
from pathlib import Path

# Create the database directory in the root directory if it doesn't exist
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_FILE = ROOT_DIR / "database" / "users.json"

# If the data file doesn't exist, create it
if not os.path.exists(DATA_FILE):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


def load_users() -> dict:
    """
    Loads all user data from the users.json file.

    Returns:
        dict: A dictionary where keys are user IDs (as strings) and values are user info.
    """
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    """
    Saves the given user dictionary into the users.json file.

    Args:
        users (dict): A dictionary of users to be saved.
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def upsert_user(user_id, username, first_name, last_name):
    """
    Adds or updates a user in the users.json file.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
    """
    users = load_users()
    users[str(user_id)] = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
    }
    save_users(users)


def get_total_users() -> int:
    """
    Returns the total number of unique users stored.

    Returns:
        int: The number of users in the system.
    """
    users = load_users()
    return len(users)
