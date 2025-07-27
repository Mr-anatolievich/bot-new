import pytest
from types import SimpleNamespace
from services.exchanges.bybit import BybitService

def test_bybit_fetch_trading_data_success(app):
    """Test BybitService._fetch_trading_data returns data for USDT pairs only."""
    service = BybitService()
    dummy_client = SimpleNamespace()
    dummy_client.get_tickers = lambda category=None: {
        "result": {
            "list": [
                {"symbol": "BTCUSDT", "bid1Price": "10000", "ask1Price": "10010", "lastPrice": "10005", "volume24h": "500", "turnover24h": "5000000", "price24hPcnt": "0.01", "highPrice24h": "10100", "lowPrice24h": "9900"},
                {"symbol": "ETHBTC", "bid1Price": "0.05", "ask1Price": "0.051"}  # non-USDT pair
            ]
        }
    }
    service.client = dummy_client
    data = service._fetch_trading_data()
    # Only BTCUSDT should appear in results
    assert "BTCUSDT" in data and data["BTCUSDT"]["bid"] == 10000.0 and data["BTCUSDT"]["ask"] == 10010.0
    assert "ETHBTC" not in data

def test_bybit_fetch_trading_data_invalid_structure(app):
    """Test BybitService._fetch_trading_data returns empty dict on missing expected keys."""
    service = BybitService()
    dummy_client = SimpleNamespace()
    # Missing 'result'
    dummy_client.get_tickers = lambda category=None: {}
    service.client = dummy_client
    assert service._fetch_trading_data() == {}
    # Missing 'list' inside result
    dummy_client.get_tickers = lambda category=None: {"result": {}}
    service.client = dummy_client
    assert service._fetch_trading_data() == {}

def test_bybit_fetch_trading_data_error(app):
    """Test BybitService._fetch_trading_data returns empty dict on exception."""
    service = BybitService()
    dummy_client = SimpleNamespace()
    dummy_client.get_tickers = lambda category=None: (_ for _ in ()).throw(Exception("API error"))
    service.client = dummy_client
    assert service._fetch_trading_data() == {}

def test_bybit_fetch_networks_data_success(app):
    """Test BybitService._fetch_networks_data returns filtered networks per coin."""
    service = BybitService()
    dummy_client = SimpleNamespace()
    dummy_client.get_coin_info = lambda: {
        "result": {
            "rows": [
                {
                    "coin": "BTC",
                    "chains": [
                        {"chain": "BTC", "chainDeposit": "1", "chainWithdraw": "0", "withdrawFee": "0.0005", "withdrawMinSize": "0.001", "confirmTimes": "2"},
                        {"chain": "Lightning", "chainDeposit": "0", "chainWithdraw": "0", "withdrawFee": "0"}
                    ]
                },
                {"coin": "ETH", "chains": []}
            ]
        }
    }
    service.client = dummy_client
    data = service._fetch_networks_data()
    # Only BTC should appear with one network (Lightning filtered out)
    assert "BTC" in data and isinstance(data["BTC"], list)
    assert any(net["name"] == "BTC" for net in data["BTC"])
    # ETH has no valid chains, so it should not be included
    assert "ETH" not in data

def test_bybit_fetch_networks_data_invalid_structure(app):
    """Test BybitService._fetch_networks_data returns empty dict on missing expected keys."""
    service = BybitService()
    dummy_client = SimpleNamespace()
    dummy_client.get_coin_info = lambda: {}
    service.client = dummy_client
    assert service._fetch_networks_data() == {}
    dummy_client.get_coin_info = lambda: {"result": {}}
    service.client = dummy_client
    assert service._fetch_networks_data() == {}

def test_bybit_fetch_networks_data_error(app):
    """Test BybitService._fetch_networks_data returns empty dict on exception."""
    service = BybitService()
    dummy_client = SimpleNamespace()
    dummy_client.get_coin_info = lambda: (_ for _ in ()).throw(Exception("API error"))
    service.client = dummy_client
    assert service._fetch_networks_data() == {}

def test_bybit_test_connection_success(app):
    """Test BybitService.test_connection returns True when server time contains expected keys."""
    service = BybitService()
    dummy_client = SimpleNamespace()
    dummy_client.get_server_time = lambda: {"result": {"timeSecond": 123456789}}
    service.client = dummy_client
    assert service.test_connection() is True

def test_bybit_test_connection_failure(app):
    """Test BybitService.test_connection returns False if client is not set or API call fails."""
    service = BybitService()
    service.client = None
    assert service.test_connection() is False
    dummy_client = SimpleNamespace()
    dummy_client.get_server_time = lambda: (_ for _ in ()).throw(Exception("Network error"))
    service.client = dummy_client
    assert service.test_connection() is False

