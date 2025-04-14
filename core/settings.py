import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

BASE_API_PATH = os.getenv("BASE_API_PATH", "/api").rstrip("/")
BASE_API_URL = os.getenv("BASE_API_URL", "http://localhost:8000/api").rstrip("/")


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
