import os


def list_log_files(dir_path) -> list:
    """
    Returns a list of log files in the given directory.
    """
    # Initialize an empty list to store the log files
    files = []
    # Check if the directory exists
    if os.path.isdir(dir_path):
        # Iterate over the files in the directory
        for name in os.listdir(dir_path):
            # include active + rotated files
            if name.endswith(".log") or ".log." in name:
                files.append(name)
    # Sort the files in reverse order (newest first)
    files.sort(reverse=True)
    return files
