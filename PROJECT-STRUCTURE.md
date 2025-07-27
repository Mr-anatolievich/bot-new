# Project Structure

├── CHANGELOG.md
├── LICENSE
├── Makefile
├── PROJECT-STRUCTURE.md
├── QUICKSTART.md
├── README.md
├── README_template.md
├── api
│   ├── __init__.py
│   ├── arbitrage.py
│   ├── dashboard.py
│   ├── exchanges.py
│   ├── notifications.py
│   ├── settings.py
│   └── websocket.py
├── app.py
├── arbitrage-bot.iml
├── cli.py
├── config
│   ├── __init__.py
│   ├── base.py
│   ├── development.py
│   ├── production.py
│   ├── settings.py
│   └── testing.py
├── docker
│   ├── Dockerfile
│   ├── docker-compose.prod.yml
│   ├── docker-compose.yml
│   └── nginx.conf
├── docs
│   ├── api.md
│   ├── architecture.md
│   ├── deployment.md
│   └── development.md
├── frontend
│   ├── App.tsx
│   ├── components
│   │   ├── Arbitrage
│   │   │   ├── ExecuteModal.tsx
│   │   │   ├── FiltersPanel.tsx
│   │   │   └── OpportunitiesTable.tsx
│   │   ├── Common
│   │   │   ├── AppHeader.tsx
│   │   │   ├── AppSidebar.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── Layout.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── LogoIcon.tsx
│   │   ├── Dashboard
│   │   │   ├── ProfitChart.tsx
│   │   │   ├── RecentTrades.tsx
│   │   │   ├── StatsCard.tsx
│   │   │   └── TopTokens.tsx
│   │   ├── Notifications
│   │   │   ├── TelegramSettings.tsx
│   │   │   ├── TemplatesEditor.tsx
│   │   │   └── TestButton.tsx
│   │   ├── PnL
│   │   │   ├── Charts.tsx
│   │   │   ├── HistoryTable.tsx
│   │   │   └── StatsPanel.tsx
│   │   ├── PositionSize
│   │   │   ├── Calculator.tsx
│   │   │   ├── InputField.tsx
│   │   │   └── ResultsCard.tsx
│   │   └── Settings
│   │       ├── AddKeyModal.tsx
│   │       ├── ApiKeysTable.tsx
│   │       └── ExchangesGrid.tsx
│   ├── hooks
│   │   ├── useApi.ts
│   │   ├── useLocalStorage.ts
│   │   ├── useNotifications.ts
│   │   ├── useTheme.ts
│   │   └── useWebSocket.ts
│   ├── services
│   │   ├── api.ts
│   │   ├── calculations.ts
│   │   ├── notifications.ts
│   │   └── websocket.ts
│   ├── types
│   │   ├── api.ts
│   │   ├── components.ts
│   │   └── index.ts
│   └── utils
│       ├── constants.ts
│       ├── formatters.ts
│       ├── helpers.ts
│       └── validators.ts
├── generate_readme.py
├── generate_structure.py
├── instance
│   └── arbitrage.db
├── jest.config.js
├── models
│   ├── __init__.py
│   ├── arbitrage_opportunity.py
│   ├── base.py
│   ├── exchange.py
│   ├── trade.py
│   └── user.py
├── package-lock.json
├── package.json
├── pydoc-markdown.yml
├── pytest.ini
├── requirements-dev.txt
├── requirements.txt
├── routes
│   ├── __init__.py
│   ├── arbitrage.py
│   ├── networks.py
│   └── tokens.py
├── run.py
├── run.sh
├── scripts
│   ├── backup.py
│   ├── deploy.sh
│   ├── health_check.py
│   └── populate_data.py
├── services
│   ├── __init__.py
│   ├── arbitrage.py
│   ├── exchanges
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── binance.py
│   │   ├── bitget.py
│   │   ├── bybit.py
│   │   ├── gateio.py
│   │   ├── huobi.py
│   │   ├── kucoin.py
│   │   ├── mexc.py
│   │   ├── okx.py
│   │   └── stub_services.py
│   ├── notifications.py
│   └── trading.py
├── setup.sh
├── static
│   ├── css
│   │   ├── index.css
│   │   └── style.css
│   ├── icons
│   │   ├── binance.svg
│   │   ├── bitget.svg
│   │   ├── bybit.svg
│   │   ├── cryptocom.svg
│   │   ├── gateio.svg
│   │   ├── huobi.svg
│   │   ├── kucoin.svg
│   │   ├── mexc.svg
│   │   └── okx.svg
│   ├── images
│   │   ├── favicon.ico
│   │   └── logo.png
│   └── js
│       ├── app.js
│       └── app.min.js
├── tailwind.config.js
├── templates
│   ├── index.html
│   └── legacy
│       ├── arbitrage.html
│       ├── base.html
│       ├── networks.html
│       └── tokens.html
├── tests
│   ├── conftest.py
│   ├── integration
│   │   └── test_services
│   │       ├── test_binance_integration.py
│   │       ├── test_bitget_integration.py
│   │       ├── test_bybit_integration.py
│   │       ├── test_gateio_integration.py
│   │       ├── test_huobi_integration.py
│   │       ├── test_kucoin_integration.py
│   │       └── test_mexc_integration.py
│   ├── test_api
│   │   ├── test_arbitrage.py
│   │   ├── test_dashboard.py
│   │   └── test_exchanges.py
│   ├── test_app.py
│   ├── test_basic.py
│   ├── test_frontend
│   │   ├── components
│   │   ├── hooks
│   │   └── services
│   └── unit
│       └── test_services
│           ├── test_binance.py
│           ├── test_bitget.py
│           ├── test_bybit.py
│           ├── test_gateio.py
│           ├── test_huobi.py
│           ├── test_kucoin.py
│           └── test_mexc.py
├── tsconfig.json
├── utils
│   ├── __init__.py
│   └── helpers.py
└── wsgi.py
