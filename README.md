# ArzWatch

ArzWatch is a Python-based web scraping application designed to fetch and store real-time price data for financial instruments (e.g., currencies like USD and EUR) from various sources (e.g., `tgju.org`, `alanchand.com`). The project supports flexible scraping via a management command (`python manage.py scrape <source> [instrument1 instrument2 ...]`) and scheduled tasks using Celery. Data is stored in a PostgreSQL database and logged to `logs/scraping.log`.

## Features

-   **Dynamic Scraping**: Scrape price data from multiple sources with configurations for multiple instruments (e.g., USD, EUR) using `SourceConfigModel`.
-   **Management Command**: Run `python manage.py scrape tgju usd eur` to scrape specific instruments or all configured instruments if none are specified.
-   **Scheduled Scraping**: Use Celery for periodic scraping of enabled sources.
-   **Database Models**:
    -   `InstrumentModel`: Stores financial instruments (e.g., USD, EUR) with categories (gold, coin, currency, crypto).
    -   `PriceTickModel`: Stores price data with timestamps and metadata.
    -   `SourceModel`: Defines scraping sources with base URLs and scraper classes.
    -   `SourceConfigModel`: Configures currencies and URL paths per source.
    -   `CurrencyModel`: Manages currency codes and names.
-   **Extensibility**: Easily add new sources (e.g., `alanchand`) via `SourceConfigModel` and custom scraper classes.
-   **Logging**: Detailed logs in `logs/scraping.log` for debugging and monitoring.

## Requirements

-   Python 3.10+
-   Django 5.1+
-   Chrome browser and compatible `chromedriver` (for Selenium)

## Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/pouria-drd/ArzWatch.git
    cd ArzWatch
    ```

2. **Set Up Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables**:
   Create a `.env` file in the project root:

    ```env
    # ---------------------------------------------------------------
    # Base URL and Admin URL Configuration
    # ---------------------------------------------------------------

    # Base URL for the API
    BASE_URL="api/"

    # Admin URL for the API (Typically used to access Django's admin panel)
    ADMIN_URL="admin/"

    # Debug mode (True for development, False for production)
    # Set to "True" during development for detailed error messages, and "False" in production for security and performance
    DEBUG="True"

    # Secret key for Django (keep this secure!)
    # This is a critical setting, keep it secret and never expose it publicly
    SECRET_KEY="your-secret-key"

    # Enable Django's debug toolbar (optional)
    # Set to "True" to enable the Django Debug Toolbar for easier debugging during development
    ENABLE_DEBUG_TOOLBAR="True"

    # ---------------------------------------------------------------
    # Time Zone and Localization Configuration
    # ---------------------------------------------------------------

    # Time zone (keep this in sync with your server)
    TIME_ZONE="UTC"

    # Enables timezone-aware datetimes in Django
    # If True, Django will store all timestamps in UTC and convert them to the user's local timezone when needed
    USE_TZ="True"

    # Enables Django's internationalization framework
    # If True, Django will support multiple languages and formats based on locale settings
    USE_I18N="True"

    # ---------------------------------------------------------------
    # Static and Media File Configuration
    # ---------------------------------------------------------------

    # Static files URL and root directory
    # URL where static files will be served from, relative to the site root
    STATIC_URL=static/
    # Path where static files will be stored after collection (useful when deploying)
    STATIC_ROOT=static

    # Media files URL and root directory
    # URL where media files (uploads) will be served from
    MEDIA_URL=/media/
    # Path where media files (uploads) will be stored on the server
    MEDIA_ROOT=media

    # ---------------------------------------------------------------
    # Host and Debugging IPs Configuration
    # ---------------------------------------------------------------

    INTERNAL_IPS=localhost,127.0.0.1,"your-internal-ips"
    ALLOWED_HOSTS=localhost,127.0.0.1,"your-allowed-hosts"

    CORS_ALLOW_CREDENTIALS=True
    CORS_ALLOWED_ORIGINS="your-allowed-origins"
    CSRF_TRUSTED_ORIGINS="your-csrf-trusted-origins"

    # ---------------------------------------------------------------
    # API Throttling Configuration
    # ---------------------------------------------------------------

    # Throttle rates for API requests
    # Throttling limits the number of requests a user can make in a given period
    USER_THROTTLE_RATE="20/minute"
    ANON_THROTTLE_RATE="10/minute"


    # ---------------------------------------------------------------
    # Email Configuration
    # ---------------------------------------------------------------

    EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST="smtp.gmail.com"
    EMAIL_PORT="587"
    EMAIL_USE_TLS="True"
    EMAIL_HOST_USER="your-host-user"
    EMAIL_HOST_PASSWORD="your-host-password"
    DEFAULT_FROM_EMAIL="your-default-from-email"
    ```

5. **Set Up `chromedriver`**:

    - Download `chromedriver` matching your Chrome version from [chromedriver.chromium.org](https://chromedriver.chromium.org/).
    - Place it in `/scraping/drivers/chromedriver.exe` (Windows) or `/scraping/drivers/chromedriver` (Linux).

6. **Apply Migrations**:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## Usage

### Run the Scrape Command

-   **Scrape all configured currencies** for a source:

    ```bash
    python manage.py scrape tgju
    ```

    **Output**:

    ```
    Scraping tgju for currencies: all...
    Successfully scraped tgju
    ```

-   **Scrape specific currencies**:

    ```bash
    python manage.py scrape tgju usd
    python manage.py scrape tgju usd eur
    ```

-   **Logs**:
    -   Check `logs/scraping.log` for details:
        ```json
        {"time": "2025-08-14 14:48:00,123", "level": "INFO", "name": "scraping.sources.tgju", "message": "Fetching data for USD from https://www.tgju.org/profile/price_dollar_rl"}
        {"time": "2025-08-14 14:48:01,124", "level": "INFO", "name": "scraping.sources.tgju", "message": "Saved price tick for USD from tgju"}
        ```

## Project Structure

```
ArzWatch/
├── arzwatch/
│   ├── management/
│   │   ├── commands/
│   │   │   ├── scrape.py
├── scraping/
│   ├── base.py
│   ├── sources/
|   |   |
│   │   ├── drivers/
│   │   │   ├── chromedriver.exe  # Windows
│   │   │   ├── chromedriver      # Linux
│   │   ├── base.py
│   │   ├── tgju.py
├── logs/
│   ├── scraping.log
├── requirements.txt
├── .env
```

## Future Enhancements

1. **API**: Develop Django REST Framework endpoints (e.g., `/api/v1/prices/latest/USD`).
2. **Telegram Bot**: Create an `aiogram` bot for commands like `/price USD`.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/xyz`).
3. Commit changes (`git commit -m 'Add feature xyz'`).
4. Push to the branch (`git push origin feature/xyz`).
5. Open a pull request.

## License

MIT License
