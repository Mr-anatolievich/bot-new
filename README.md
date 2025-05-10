# Arbitrage Bot

Arbitrage Bot is a web platform for cryptocurrency arbitrage across multiple exchanges. It fetches live price and network data from various exchange APIs to detect profitable arbitrage opportunities. The platform is built using Python (Flask) for the backend and Jinja2 + HTML/CSS/JS for the frontend.

---

## 🚀 Features

- Fetches **buy/sell prices** and **network data** from multiple exchanges.
- Calculates and displays **profitable arbitrage spreads**.
- Auto-refreshes price data for real-time updates.
- Provides filters for **tokens** and **networks**.
- Visual presentation with **exchange icons** and colored profit indicators.

---

## 🛠️ Tech Stack

### Backend
- **Python** (Flask)
- **APIs**: Binance, Bybit, KuCoin, Gate.io, Huobi, MEXC, Bitget
- **Environment Management**: `python-dotenv`

### Frontend
- **HTML** (Jinja2 templates)
- **CSS** (Custom styles)
- **JavaScript** (AJAX for dynamic updates)

### Tools
- **Testing**: `pytest`
- **Security**: `flask-talisman`, `.env` for secrets
- **Version Control**: Git

---

## 📂 Project Structure

```
arbitrage-bot/
├── app.py                # Main Flask app (entry point)
├── requirements.txt      # Python dependencies
├── static/               # Icons & CSS
│   ├── *.svg             # Exchange icons
│   └── style.css         # Stylesheet
├── templates/            # HTML templates
│   ├── base.html         # Global layout
│   ├── index.html        # Homepage with arbitrage table
│   ├── arbitrage.html    # Arbitrage opportunities
│   ├── tokens.html       # Token-by-exchange display
│   ├── networks.html     # Withdrawal networks and fees
│   ├── table_body.html   # Partial for arbitrage rows
│   └── tokens_table_body.html # Partial for token tables
└── .env                  # Environment variables (not committed)
```

---

## 🔌 Supported Exchanges

- Binance
- Bybit
- KuCoin
- Gate.io
- Huobi
- MEXC
- Bitget

---

## 🖥️ Setup Instructions

### Prerequisites
- Python 3.8+
- `pip` (Python package manager)
- Node.js (optional, for frontend development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/arbitrage-bot.git
   cd arbitrage-bot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your API keys for the supported exchanges:
     ```
     BINANCE_API_KEY=your_binance_api_key
     BINANCE_API_SECRET=your_binance_api_secret
     # Add other exchange keys here
     ```

5. Run the Flask app:
   ```bash
   flask run
   ```

6. Open the app in your browser:
   ```
   http://127.0.0.1:5000
   ```

---

## 🧪 Testing

1. Install testing dependencies:
   ```bash
   pip install pytest requests-mock
   ```

2. Run tests:
   ```bash
   pytest
   ```

---

## ✨ Future Improvements

- Add PostgreSQL/SQLite database for historical data.
- User authentication for managing API keys.
- Periodic syncs using Celery or APScheduler.
- Enhanced UI with advanced filtering and sorting.

---

## 🔐 Security Notes

- API keys are stored in `.env` and never committed to the repository.
- Use `flask-talisman` to enforce secure headers (CSP, HSTS).
- Avoid rendering sensitive error details in production.

---

## 📄 Documentation

- **Code Documentation**: Inline docstrings (PEP257)
- **Setup Guide**: See above
- **Changelog**: Refer to `CHANGELOG.md` for version history
