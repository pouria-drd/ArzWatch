# ArzWatch

A Python-based currency and price monitoring tool that fetches and displays real-time market data from website like TGJU (Tehran Gold and Jewelry Union) and other ones.

## Features

-   Real-time price fetching from TGJU
-   Multiple display formats (table and name-value pairs)
-   Support for both Rial and Toman currency display
-   Clean and organized terminal output
-   Modular architecture for easy extension

## Installation

1. Clone the repository:

```bash
git clone https://github.com/pouria-drd/ArzWatch.git
cd ArzWatch
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. **Set Up Environment Variables:**

    Create a `.env` file in the project root and add the following:

    ```ini

    USE_TOMAN="True" # or False to use Rial

    PRINT_TYPE="table" # or name_value

    ```

## Usage

Run the main script:

```bash
python main.py
```

### Configuration

You can modify the following settings in `main.py`:

-   `use_toman`: Set to `True` to display prices in Toman, `False` for Rial
-   `print_type`: Choose between "table" or "name_value" display format

## Project Structure

```
ArzWatch/
├── main.py              # Main application entry point
├── requirements.txt     # Project dependencies
├── fetchers/           # Data fetching modules
├── formatters/         # Data formatting modules
└── utils/              # Utility functions and helpers
```

## Dependencies

-   beautifulsoup4: For parsing HTML content
-   requests: For making HTTP requests
-   tabulate: For table formatting
-   termcolor: For colored terminal output

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
