# Arbitrage Bot Feature Overview

Arbitrage Bot is a web platform for monitoring arbitrage opportunities across cryptocurrency exchanges, taking into account fees, withdrawal networks, buy/sell prices, and available balances. The interface consists of several tabs:

---

## 📌 Preconditions

* We work with the following exchanges: `binance`, `kucoin`, `bybit`, `gate`, `okx`, `bitget`, `huobi`.
* For each exchange, data is retrieved for tokens paired with **USDT**.
* The following data is stored in the database for each token:

  * **Sell price (ask)**
  * **Buy price (bid)**
  * **Available withdrawal networks**
  * **Withdrawal network fee**
  * **Trading volume on the exchange for this token**

---

## 📊 Dashboard

* **Total Balance (\$)**: total balance across all exchanges, calculated in USDT or USDC. Shows 24-hour change.
* **Wallet Breakdown**: donut chart showing the distribution of assets across exchanges. Hover to see available, frozen, and total balances.
* **PnL Today / MTD (Month-to-Date)**: KPI cards showing gross profit, fees, and net profit. Profits are highlighted in green, losses in red.
* **Performance Chart**: line chart showing performance over the selected period.

---

## 🔀 Arbitrage

* Displays arbitrage opportunities between exchanges, filtered by profitability (>0.1%).
* Table columns include:

  * **Currency pair** (e.g., BTC/USDT)
  * **Buy exchange** and **token price for purchase**
  * **Sell exchange** and **token price for sale**
  * **Volume** — 24-hour trading volume on the buy exchange
  * **Profit (%)** — calculated profit margin
  * **Deal lifetime** — how long the opportunity remains valid
  * **Networks** — available networks for withdrawal and deposit of this token
* Profit is shown in green, loss in red.
* Supports automatic table refresh at a specified interval.

---

## ⚙️ Trade Execution Algorithm

1. Identify a trading pair with a spread between exchange A (buy) and exchange B (sell).
2. Create a **market order** to buy the token on exchange A.
3. Confirm the token is **successfully purchased** and appears in the wallet on exchange A.
4. **Transfer the token** from exchange A to exchange B via the selected network.
5. Wait for confirmation — token is **credited to exchange B** (this may take time).
6. Create a **limit order to sell** the token on exchange B, where the price is calculated as:

   **Sell price = Buy price (A) + Purchase fee + Network fee + Fixed spread at time of opportunity detection**

---

## 📏 Position Size

This tab allows the user to select how to calculate the position size for opening an arbitrage trade.

* **Mode Selector**:

  * **Fixed amount** — input a specific amount in USD (minimum \$10). This amount is used as the fixed trade size.
  * **Percent of free balance** — select a percentage (1–100%) of the available USDT wallet balance. This mode allows dynamic risk management.

* **Save** — the selected value is saved to the database and applied when the **"Execute"** button is pressed.

---

## 📈 History

> ⚠️ **Problem to solve:** If the token price drops after buying on exchange A and transferring to exchange B, what should be done?
>
> * Sell immediately and take the loss?
> * Wait for the price to recover?
> * Set up a dynamic strategy with stop-limit orders or algorithmic trading?

This tab displays a table of all completed arbitrage trades. Data is retrieved from the database, which stores every buy and sell operation. Table columns include:

\| | Date/Time     | Market      | Exchange (Buy→Sell) | Volume \$ | 1st/2nd price     | Status |
\|---------------|-------------|---------------------|----------|-------------------|--------|

* **Date/Time** — timestamp of the operation.
* **Market** — currency pair (e.g., ETH/USDT).
* **Exchange (Buy→Sell)** — buy exchange → sell exchange.
* **Volume \$** — trade volume in USD.
* **1st/2nd price** — buy and sell prices.
* **Status** — trade status (success, error, etc.).

---

## 🔐 Security

* API keys are stored in the `.env` file, which is not included in the repository.
* Planned IP whitelisting for enhanced protection.
* Uses `flask-talisman` for secure headers (CSP, HSTS).

---

## 🔔 Notifications

**The notification system via Telegram bot includes the following message templates:**

* ✅ **Trade Executed** — notification about a completed trade:

  ```
  💰 Trade Executed!
  🔄 Bought on: {{ buy_exchange }}
  💸 Sold on: {{ sell_exchange }}
  📈 Profit: {{ profit_percent }}%
  📊 Volume: {{ volume_usd }} USDT
  🕒 {{ timestamp }}
  ```

* ✅ **Daily Balance Summary (08:00 UTC)** — daily balance report:

  ```
  📊 Daily Balance Summary
  💼 Exchange: {{ exchange_name }}
  💵 Balance: {{ balance }} USDT
  🔒 Frozen: {{ frozen }} USDT
  🟢 Available: {{ available }} USDT
  📅 {{ date }}
  ```

* ⚠️ **Low Wallet Balance** — low balance warning:

  ```
  🚨 Low Wallet Balance!
  👛 Exchange: {{ exchange_name }}
  🔻 Current Balance: {{ balance }} USDT
  🧯 Minimum Threshold: {{ threshold }} USDT
  ```

* ❌ **API Key Error / IP Mismatch** — authorization error:

  ```
  ❗️Authorization Error
  🔐 Exchange: {{ exchange_name }}
  📛 Reason: {{ error_message }}
  📍 IP: {{ current_ip }}
  🔄 Check your API key or allowed IPs
  ```

* 🧪 **Test Message** — test notification:

  ```
  ✅ Test Message
  This is a test notification from the Telegram bot.
  Everything is working fine! 🚀
  ```

---

## 🆕 Exchanges

* Supported exchanges: Binance, Bybit, OKX, KuCoin, Gate.io, Huobi, MEXC, Bitget.
* Tokens per exchange are displayed with bid/ask prices, trading volume, and available networks.
* Data auto-refresh is supported.
* Tabs with exchange logos.
