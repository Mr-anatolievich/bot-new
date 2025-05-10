# Copilot Instructions for Arbitrage Bot (Python Flask Project)

## 🧠 Project Overview

This project is a **web platform for cryptocurrency arbitrage** across multiple exchanges. It uses Python (Flask) as the backend framework and Jinja2 + HTML/CSS/JS for rendering views. The app pulls live price and network data from APIs of various exchanges to detect profitable arbitrage opportunities.

---

## 🗂️ Project Structure (Important Files)

arbitrage-bot/
├── app.py # Main Flask app (entry point)
├── requirements.txt # Python dependencies
├── package.json # (Optional) JS-related metadata
├── static/ # Icons & CSS
│ ├── *.svg # Exchange icons
│ └── style.css # Stylesheet
├── templates/ # HTML templates
│ ├── base.html # Global layout
│ ├── index.html # Homepage with arbitrage table
│ ├── arbitrage.html # Arbitrage opportunities
│ ├── tokens.html # Token-by-exchange display
│ ├── networks.html # Withdrawal networks and fees
│ ├── table_body.html # Partial for arbitrage rows
│ └── tokens_table_body.html# Partial for token tables
---

## 🔌 API Integrations

APIs integrated in `app.py`:

* **Binance** via `python-binance`
* **Bybit** via `pybit`
* **KuCoin** via `python-kucoin`
* **Gate.io** via `gate-api`
* **Huobi** via `huobi`
* **MEXC** via `mexc-api`
* **Bitget** via `python-bitget`

Environment variables for API keys are managed with `.env` and `python-dotenv`.

---

## ✅ Key Functionality

* Fetches **buy/sell prices** and **networks** across exchanges
* Calculates and displays **profitable arbitrage spreads**
* Allows **auto-refreshing** price data
* Provides filters for **tokens** and **networks**
* Visual presentation using **exchange icons**, colored profit indicators

---

## 💡 Coding Guidelines for Copilot

### Python (Flask Backend)

* Use `@app.route(...)` to define new routes
* Use `render_template()` with Jinja2 HTML
* Read API keys with `os.getenv(...)`
* Group logic in functions (e.g. `fetch_binance_data()`)

### 🧩 Modularization Instructions

Split `app.py` logic into modules:

```
project/
├── app.py                # Minimal app runner only
├── routes/               # Route definitions
│   ├── arbitrage.py
│   ├── tokens.py
│   └── networks.py
├── services/             # Business logic and data fetchers
│   ├── binance.py
│   ├── bybit.py
│   ├── kucoin.py
│   └── ...
├── utils/                # Shared utilities (e.g. formatting, error handling)
│   └── helpers.py
├── templates/            # HTML views (Jinja2)
└── static/               # Icons and CSS
```

* Import Flask `Blueprint` objects from `routes/`
* Move API-fetching functions into `services/`
* Use `__init__.py` for `routes/` and `services/` to make them packages

### HTML/Jinja2

* Reuse layout from `base.html` via `{% extends "base.html" %}`
* Dynamic values: `{{ variable }}`
* Loops: `{% for item in list %}...{% endfor %}`
* Safe HTML: `|safe` or escaping is automatic

### JavaScript

* Auto-refresh: use `setInterval(fetchTable, seconds * 1000)`
* AJAX: fetch partial views (`table_body.html`, etc.)
* DOM manipulation for UI updates (e.g., tabs, filters)

---

## 🔐 Security Notes

* API keys must **never** be committed to code
* Use `.env` and `.gitignore` to manage secrets
* Consider adding Flask `Flask-Limiter` for rate limiting

---

## 🧪 Testing Suggestions

* Unit test each exchange API wrapper
* Simulate network failure and malformed responses
* Test sorting logic and UI behavior with sample data

---

## ✨ Improvements to Consider

* Add PostgreSQL/SQLite DB for history
* Authentication for user-specific API key management
* Integrate Celery or APScheduler for periodic syncs

---
