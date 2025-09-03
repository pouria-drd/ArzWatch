import os


def list_apps(settings) -> list:
    """
    Returns a list of app names and their log directories.
    """
    # Get the log directories from the settings
    d = getattr(settings, "APP_LOG_DIRS", {})
    # Get the app names and paths
    items = [(app, path) for app, path in d.items() if os.path.isdir(path)]
    # Sort the items by app name
    items.sort(key=lambda x: x[0])
    return items
