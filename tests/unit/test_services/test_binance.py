import pytest
from types import SimpleNamespace
from services.exchanges.binance import BinanceService

def test_binance_fetch_trading_data_success(app):
    """Test BinanceService._fetch_trading_data returns filtered and normalized data for USDT pairs."""
    service = BinanceService()
    # Create dummy client with get_ticker returning sample data
    dummy_client = SimpleNamespace()
    dummy_client.get_ticker = lambda: [
        {"symbol": "BTCUSDT", "bidPrice": "50000", "askPrice": "50100", "lastPrice": "50050", "volume": "100", "quoteVolume": "5000000", "priceChange": "100", "priceChangePercent": "0.2", "count": "42"},
        {"symbol": "ETHBTC", "bidPrice": "10", "askPrice": "11", "lastPrice": "10.5", "volume": "200", "quoteVolume": "2000", "priceChange": "0.1", "priceChangePercent": "1", "count": "10"},  # non-USDT pair
        {"symbol": "XRPUSDT", "bidPrice": "0", "askPrice": "0.5", "lastPrice": "0.5", "volume": "1000", "quoteVolume": "500", "priceChange": "0", "priceChangePercent": "0", "count": "5"}  # zero bid price, should skip
    ]
    service.client = dummy_client  # Patch client to dummy
    data = service._fetch_trading_data()
    # Only BTCUSDT should be included (XRPUSDT skipped due to zero bid, ETHBTC skipped due to non-USDT)
    assert "BTCUSDT" in data and data["BTCUSDT"]["symbol"] == "BTCUSDT"
    assert data["BTCUSDT"]["bid"] == 50000.0 and data["BTCUSDT"]["ask"] == 50100.0
    assert "ETHBTC" not in data
    assert "XRPUSDT" not in data

def test_binance_fetch_trading_data_error(app):
    """Test BinanceService._fetch_trading_data returns empty dict on exception."""
    service = BinanceService()
    service.client = SimpleNamespace()
    service.client.get_ticker = lambda: (_ for _ in ()).throw(Exception("API error"))
    result = service._fetch_trading_data()
    assert result == {}

def test_binance_fetch_networks_data_success(app):
    """Test BinanceService._fetch_networks_data returns network data organized by coin."""
    service = BinanceService()
    dummy_client = SimpleNamespace()
    dummy_client.get_all_coins_info = lambda: [
        {
            "coin": "BTC",
            "networkList": [
                {"network": "BTC", "depositEnable": True, "withdrawEnable": False, "withdrawFee": "0.001", "withdrawMin": "0.01", "withdrawMax": "10", "minConfirm": 2, "unLockConfirm": 0},
                {"network": "Lightning", "depositEnable": False, "withdrawEnable": False, "withdrawFee": "0"}
            ]
        },
        {"coin": "ETH", "networkList": []}
    ]
    service.client = dummy_client
    data = service._fetch_networks_data()
    # Should include BTC with one network (Lightning filtered out because no deposit/withdraw)
    assert "BTC" in data and isinstance(data["BTC"], list)
    assert any(net["name"] == "BTC" for net in data["BTC"])
    # ETH has no enabled networks, so should not appear
    assert "ETH" not in data

def test_binance_fetch_networks_data_error(app):
    """Test BinanceService._fetch_networks_data returns empty dict on error."""
    service = BinanceService()
    service.client = SimpleNamespace()
    service.client.get_all_coins_info = lambda: (_ for _ in ()).throw(Exception("API error"))
    result = service._fetch_networks_data()
    assert result == {}

def test_binance_get_account_info_success(app):
    """Test BinanceService.get_account_info returns formatted balance and status info."""
    service = BinanceService()
    dummy_client = SimpleNamespace()
    dummy_account = {
        "canTrade": True, "canWithdraw": False, "canDeposit": True, "updateTime": 1234567890,
        "balances": [
            {"asset": "BTC", "free": "1.5", "locked": "0.5"},   # total = 2.0 (included)
            {"asset": "ETH", "free": "0", "locked": "0"}        # total = 0 (filtered out)
        ]
    }
    dummy_client.get_account = lambda: dummy_account
    service.client = dummy_client
    info = service.get_account_info()
    # Overall status flags
    assert info["trading_status"] is True and info["withdraw_status"] is False and info["deposit_status"] is True
    # Only BTC balance should be included
    assert info["total_assets"] == 1
    assert info["balances"][0]["asset"] == "BTC" and info["balances"][0]["total"] == 2.0

def test_binance_get_account_info_no_client(app):
    """Test BinanceService.get_account_info returns empty dict when client is not initialized."""
    service = BinanceService()
    service.client = None
    assert service.get_account_info() == {}

def test_binance_get_account_info_error(app):
    """Test BinanceService.get_account_info returns empty dict on exception."""
    service = BinanceService()
    dummy_client = SimpleNamespace()
    dummy_client.get_account = lambda: (_ for _ in ()).throw(Exception("API error"))
    service.client = dummy_client
    assert service.get_account_info() == {}

def test_binance_get_exchange_info_success(app):
    """Test BinanceService.get_exchange_info returns filtered symbol info for USDT pairs."""
    service = BinanceService()
    dummy_client = SimpleNamespace()
    dummy_exchange_info = {
        "timezone": "UTC", "serverTime": 1620000000000,
        "symbols": [
            {
                "symbol": "BTCUSDT", "status": "TRADING", "baseAsset": "BTC", "quoteAsset": "USDT",
                "orderTypes": ["LIMIT", "MARKET"], "isSpotTradingAllowed": True,
                "filters": [
                    {"filterType": "PRICE_FILTER", "minPrice": "0.01", "maxPrice": "100000", "tickSize": "0.01"},
                    {"filterType": "LOT_SIZE", "minQty": "0.0001", "maxQty": "1000", "stepSize": "0.0001"},
                    {"filterType": "MIN_NOTIONAL", "minNotional": "10"}
                ]
            },
            {
                "symbol": "ETHBTC", "status": "TRADING", "baseAsset": "ETH", "quoteAsset": "BTC",
                "orderTypes": ["LIMIT", "MARKET"], "isSpotTradingAllowed": True,
                "filters": []
            }
        ]
    }
    dummy_client.get_exchange_info = lambda: dummy_exchange_info
    service.client = dummy_client
    info = service.get_exchange_info()
    # Only BTCUSDT should be present in symbols
    assert info["symbols_count"] == 1 and "BTCUSDT" in info["symbols"]
    sym_info = info["symbols"]["BTCUSDT"]
    assert sym_info["base_asset"] == "BTC" and sym_info["quote_asset"] == "USDT"
    # Filters parsed correctly
    assert "price" in sym_info["filters"] and "quantity" in sym_info["filters"] and "notional" in sym_info["filters"]

def test_binance_get_exchange_info_no_client(app):
    """Test BinanceService.get_exchange_info returns empty dict when client is not initialized."""
    service = BinanceService()
    service.client = None
    assert service.get_exchange_info() == {}

def test_binance_get_exchange_info_error(app):
    """Test BinanceService.get_exchange_info returns empty dict on exception."""
    service = BinanceService()
    dummy_client = SimpleNamespace()
    dummy_client.get_exchange_info = lambda: (_ for _ in ()).throw(Exception("API error"))
    service.client = dummy_client
    assert service.get_exchange_info() == {}

def test_binance_test_connection_success(app):
    """Test BinanceService.test_connection returns True when ping and account call succeed."""
    service = BinanceService()
    dummy_client = SimpleNamespace()
    dummy_client.ping = lambda: True
    dummy_client.get_account = lambda: {"balances": []}
    service.client = dummy_client
    assert service.test_connection() is True

def test_binance_test_connection_failure(app):
    """Test BinanceService.test_connection returns False if client not initialized or API call fails."""
    service = BinanceService()
    service.client = None
    assert service.test_connection() is False
    dummy_client = SimpleNamespace()
    dummy_client.ping = lambda: (_ for _ in ()).throw(Exception("Ping failed"))
    dummy_client.get_account = lambda: {"balances": []}
    service.client = dummy_client
    assert service.test_connection() is False

def test_binance_get_health_status(app):
    """Test BinanceService.get_health_status reflects client and connection status."""
    service = BinanceService()
    service.client = object()  # Simulate client initialized
    # Case 1: connected
    service.test_connection = lambda: True
    status = service.get_health_status()
    assert status["name"] == "Binance"
    assert status["available"] is True  # BINANCE_AVAILABLE should be True if library installed
    assert status["client_initialized"] is True and status["connected"] is True
    assert isinstance(status["trading_cache_age"], int) and isinstance(status["networks_cache_age"], int)
    assert status["last_error"] is None
    # Case 2: disconnected
    service.test_connection = lambda: False
    status2 = service.get_health_status()
    assert status2["connected"] is False

