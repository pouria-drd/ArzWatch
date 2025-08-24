# ArzWatch

**ArzWatch** is a modular Django app that scrapes **currency, gold, coin, and crypto** prices from multiple sources, stores them in SQL, and exposes clean endpoints. Built with **Selenium + BeautifulSoup**, designed to be **fast to extend** and **easy to run**.

---

## ✨ Features

-   **Modular scrapers**: `tgju`, `wallex`, `zarminex` (add more in minutes)
-   **Default‑first logic** per instrument (use active default source → else fallback)
-   **Single, unified CLI**: `manage.py scrape`
-   **Accurate decimals** for crypto + rich `meta` JSON
-   **Django + DRF** API ready
-   Logging hooks and structured error handling

---

## 🏗 Architecture

```
arzwatch/
  scraping/
    management/commands/
      scrape.py            # unified CLI (default‑first logic)
    sources/
      base.py
      tgju.py
      wallex.py
      zarminex.py
    api/
      serializers/
      views/
```

**Core models**

-   `InstrumentModel(symbol, category, default_source, enabled)`
-   `SourceModel(name, base_url, enabled)`
-   `SourceConfigModel(source, instrument, path)`
-   `PriceTickModel(price, currency, timestamp, meta)`

---

## 📋 Requirements

-   Python **3.10+**, Django **4/5**
-   PostgreSQL (recommended) or SQLite
-   Google Chrome + ChromeDriver (Selenium)

> No local driver? Use `--auto-driver` and we’ll install one on the fly.

---

## ⚙️ Installation

```bash
# 1) Clone & env
git clone https://github.com/pouria-drd/ArzWatch.git
cd ArzWatch
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) DB setup
python manage.py migrate

# 4) Run API
python manage.py runserver
```

---

## 🔐 Configuration (.env)

Create a `.env` at project root (values are examples):

```env
# ----------------------------------------------------------------------------
# Django
# ----------------------------------------------------------------------------
DEBUG=True
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=UTC
USE_TZ=True

# ----------------------------------------------------------------------------
# URLs
# ----------------------------------------------------------------------------
BASE_URL=api/
ADMIN_URL=admin/

# ----------------------------------------------------------------------------
# CORS / CSRF (adjust for production)
# ----------------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOWED_ORIGINS=http://localhost:8000
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# ----------------------------------------------------------------------------
# Static / Media
# ----------------------------------------------------------------------------
STATIC_URL=/static/
STATIC_ROOT=static
MEDIA_URL=/media/
MEDIA_ROOT=media

# ----------------------------------------------------------------------------
# DRF Throttling (example rates)
# ----------------------------------------------------------------------------
USER_THROTTLE_RATE=20/minute
ANON_THROTTLE_RATE=10/minute
SCRAPING_THROTTLE_RATE=60/minute

# ----------------------------------------------------------------------------
# Email (optional)
# ----------------------------------------------------------------------------
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=app-password-here
DEFAULT_FROM_EMAIL=you@example.com


# ----------------------------------------------------------------------------
# Scraping
# ----------------------------------------------------------------------------
SCRAPING_SLEEP_TIME=5

# ---------------------------------------------------------------
# Telegram Configuration
# ---------------------------------------------------------------
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_PROXY_URL=your-sock5-proxy-url-here
```

> Tip: keep `.env` out of version control. Commit a `.env.example` instead.

---

## 🧰 Unified Scrape Command

Default‑first behavior:

-   If an instrument has an **active default source** → scrape **only** that.
-   Otherwise use the **first active configured fallback**.
-   If none → **warn & skip**.

### Source scope

```bash
# All enabled sources (each uses its configured instruments)
python manage.py scrape --source

# Only one source
python manage.py scrape --source tgju
```

### Instrument scope

```bash
# All enabled instruments (each: default‑first → fallback)
python manage.py scrape --instrument

# Only one instrument (USD)
python manage.py scrape --instrument usd

# USD from a specific source
python manage.py scrape --instrument usd --source wallex

# USD from all its active sources
python manage.py scrape --instrument usd --source
```

> `--auto-driver` works with any mode to auto-install ChromeDriver.

---

## 📡 API (starter)

-   `GET /api/instruments/?category=crypto` → list instruments with latest ticks
-   `GET /api/sources/` → list sources with latest ticks

(Adjust to your app paths; serializers/views are ready to extend.)

---

## ➕ Add a New Source

1. Create `scraping/sources/<name>.py` implementing `BaseScraper.fetch_data()`.
2. Add the scraper to `SCRAPER_MAP` in `scrape.py`.
3. Insert `SourceModel` + `SourceConfigModel` rows.
4. Test run: `python manage.py scrape --source <name>`.

---

## 🧪 Troubleshooting

-   **Driver errors** → run with `--auto-driver` or match Chrome/Driver versions.
-   **Scraping errors** → check `logs/scraping.log` for details.
-   **API errors** → check `logs/scraping_api.log` for details.

---

## 🗺 Roadmap

-   Telegram bot
-   API endpoints
-   More scrapers

---

## 📜 License

MIT
