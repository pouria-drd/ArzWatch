# ArzWatch

A Python-based currency and price monitoring tool with Telegram bot integration that fetches and displays real-time market data from websites like [Alan Chand](https://alanchand.com/gold-price) and other sources.

## Features

-   Real-time price fetching from [Alan Chand](https://alanchand.com/gold-price) and other sources
-   Telegram bot integration for easy access to price information
-   Support for both Rial and Toman currency display
-   Clean and organized terminal output
-   Modular architecture for easy extension
-   Logging system for monitoring and debugging

## Installation

### Windows

```bash
# Clone the repository
git clone https://github.com/pouria-drd/ArzWatch.git
cd ArzWatch

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### macOS

```bash
# Clone the repository
git clone https://github.com/pouria-drd/ArzWatch.git
cd ArzWatch

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Linux

```bash
# Clone the repository
git clone https://github.com/pouria-drd/ArzWatch.git
cd ArzWatch

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

After installation on any platform, create a `.env` file in the project root and add the following:

```ini
BASE_API_URL="YOUR_BASE_API_URL"
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
```

## Usage

Run the main script:

```bash
python main.py
```

This will start the Telegram bot service which can be used to fetch real-time price information.

## Project Structure

```
ArzWatch/
├── main.py              # Main application entry point
├── requirements.txt     # Project dependencies
├── .env                # Environment configuration file
├── .gitignore          # Git ignore rules
├── bots/               # Telegram bot implementation
├── database/           # Database related files
├── logger/             # Logging configuration and utilities
├── logs/               # Log files directory
├── scrapers/           # Web scraping modules
└── .venv/              # Python virtual environment
```

## Dependencies

Key dependencies include:

-   python-telegram-bot: For Telegram bot functionality
-   beautifulsoup4: For parsing HTML content
-   requests: For making HTTP requests
-   httpx: For async HTTP requests
-   python-dotenv: For environment variable management
-   tabulate: For table formatting
-   colorlog: For colored logging output

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
