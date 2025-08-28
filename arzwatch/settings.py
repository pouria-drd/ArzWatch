import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "arzwatch-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party apps
    "corsheaders",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    # Custom apps
    "bot",
    "scraping",
    "api_key",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
    "django.middleware.security.SecurityMiddleware",  # Security middleware
    "django.contrib.sessions.middleware.SessionMiddleware",  # Session middleware
    "django.middleware.common.CommonMiddleware",  # Common middleware
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Authentication middleware
    "django.contrib.messages.middleware.MessageMiddleware",  # Message middleware
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Prevent clickjacking
]

# Debug Toolbar (optional)
ENABLE_DEBUG_TOOLBAR = os.getenv("ENABLE_DEBUG_TOOLBAR", "False").lower() == "true"
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")  # Add debug toolbar to apps
    MIDDLEWARE.insert(
        0, "debug_toolbar.middleware.DebugToolbarMiddleware"
    )  # Add debug toolbar to middleware

ROOT_URLCONF = "arzwatch.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # "DIRS": [],
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "arzwatch.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "arzwatchDB.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = os.getenv("TIME_ZONE", "UTC")

USE_I18N = os.getenv("USE_I18N", "True") == "True"

USE_TZ = os.getenv("USE_TZ", "True") == "True"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Static files URL and root directory
STATIC_URL = os.getenv("STATIC_URL", "static/")  # Default is "static/"
STATIC_ROOT = os.path.join(BASE_DIR, os.getenv("STATIC_ROOT", "static"))

# Media files URL and root directory
MEDIA_URL = os.getenv("MEDIA_URL", "/media/")  # Default is "/media/"
MEDIA_ROOT = BASE_DIR / os.getenv("MEDIA_ROOT", "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------
# Allowed Hosts Configuration
# ---------------------------------------------------------------
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(
    ","
)  # Allowed hosts from environment variable

INTERNAL_IPS = os.getenv("INTERNAL_IPS", "127.0.0.1").split(
    ","
)  # Internal IPs for debug toolbar

# ---------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "False") == "True"
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]  # Allowed HTTP methods for CORS

# ---------------------------------------------------------------
# Django REST Framework Configuration
# ---------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        # "rest_framework.permissions.IsAuthenticated",  # Only authenticated users can access
        "rest_framework.permissions.IsAdminUser",  #  Allow anonymous users to access
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",  # Throttle based on user rate
        "rest_framework.throttling.AnonRateThrottle",  # Throttle based on anonymous user rate
        "rest_framework.throttling.ScopedRateThrottle",  # Throttle based on scope
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("ANON_THROTTLE_RATE", "10/minute"),
        "user": os.getenv("USER_THROTTLE_RATE", "20/minute"),
        "scraping": os.getenv("SCRAPING_THROTTLE_RATE", "60/minute"),
    },
}

# ---------------------------------------------------------------
# SPECTACULAR Configuration
# ---------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "ArzWatch API",
    "DESCRIPTION": "API for ArzWatch",
    "VERSION": "0.0.1",
    "SERVE_INCLUDE_SCHEMA": False,
    # OTHER SETTINGS
}

# ---------------------------------------------------------------
# Email Configuration
# ---------------------------------------------------------------
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


# ---------------------------------------------------------------
# Scraping Configuration
# ---------------------------------------------------------------
SCRAPING_SLEEP_TIME = int(os.getenv("SCRAPING_SLEEP_TIME", 5))

# ---------------------------------------------------------------
# Telegram Configuration
# ---------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", None)
TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL", None)
# TELEGRAM_PROXY_URL = None

# ---------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
        },
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "arzwatch.log"),
            "formatter": "json",
        },
        "scraping_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "scraping.log"),
            "formatter": "json",
        },
        "scraping_api_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "scraping_api.log"),
            "formatter": "json",
        },
        "telegram_bot_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "telegram_bot.log"),
            "formatter": "json",
        },
        "api_key_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "api_key.log"),
            "formatter": "json",
        },
    },
    "loggers": {
        # "": {
        #     "handlers": ["console", "file"],
        #     "level": "INFO",
        #     "propagate": False,
        # },
        # "django": {
        #     "handlers": ["console", "file"],
        #     "level": "INFO",
        #     "propagate": False,
        # },
        "scraping": {
            "handlers": ["console", "scraping_file"],
            "level": "INFO",
            "propagate": False,
        },
        "scraping_api": {
            "handlers": ["console", "scraping_api_file"],
            "level": "INFO",
            "propagate": False,
        },
        "telegram_bot": {
            "handlers": ["console", "telegram_bot_file"],
            "level": "INFO",
            "propagate": False,
        },
        "api_key": {
            "handlers": ["console", "api_key_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
