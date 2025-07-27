import pytest
import requests
from types import SimpleNamespace
from services.exchanges.kucoin import KucoinService

class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
    def json(self):
        return self._data

def test_kucoin_fetch_trading_data_success(app):
    """Test KucoinService._fetch_trading_data returns data for USDT pairs with proper filtering."""
    service = KucoinService()
    dummy_client = SimpleNamespace()
    dummy_client.get_tickers = lambda: {
        "ticker": [
            {"symbol": "BTC-USDT", "buy": "30000", "sell": "30100", "last": "30050", "vol": "1000", "volValue": "30000000", "changeRate": "0.05", "high": "31000", "low": "29000"},
            {"symbol": "ETH-BTC", "buy": "0.07", "sell": "0.071"},
            {"symbol": "LTC-USDT", "buy": "0", "sell": "100"}
        ]
    }
    service.client = dummy_client
    data = service._fetch_trading_data()
    # Only BTCUSDT should be present
    assert "BTCUSDT" in data and data["BTCUSDT"]["bid"] == 30000.0 and data["BTCUSDT"]["ask"] == 30100.0
    assert "ETHBTC" not in data and "LTCUSDT" not in data

def test_kucoin_fetch_trading_data_invalid_structure(app):
    """Test KucoinService._fetch_trading_data returns empty dict if 'ticker' key missing."""
    service = KucoinService()
    dummy_client = SimpleNamespace()
    dummy_client.get_tickers = lambda: {"wrong_key": []}
    service.client = dummy_client
    assert service._fetch_trading_data() == {}

def test_kucoin_fetch_trading_data_error(app):
    """Test KucoinService._fetch_trading_data returns empty dict on exception."""
    service = KucoinService()
    dummy_client = SimpleNamespace()
    dummy_client.get_tickers = lambda: (_ for _ in ()).throw(Exception("API error"))
    service.client = dummy_client
    assert service._fetch_trading_data() == {}

def test_kucoin_fetch_networks_data_success(app, monkeypatch):
    """Test KucoinService._fetch_networks_data returns network info for currencies."""
    service = KucoinService()
    dummy_data = {
        "code": "200000",
        "data": [
            {
                "currency": "BTC",
                "chains": [
                    {"chainName": "BTC", "isDepositEnabled": True, "isWithdrawEnabled": False, "withdrawalMinFee": "0.0005", "withdrawalMinSize": "0.001", "confirms": 2},
                    {"chainName": "Lightning", "isDepositEnabled": False, "isWithdrawEnabled": True, "withdrawalMinFee": "0", "withdrawalMinSize": "0", "confirms": 1}
                ]
            },
            {
                "currency": "ETH",
                "chains": [
                    {"chainName": "ETH", "isDepositEnabled": False, "isWithdrawEnabled": False}
                ]
            }
        ]
    }
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_networks_data()
    # BTC should be included with both networks (BTC and Lightning)
    assert "BTC" in data
    networks = data["BTC"]
    names = [net["name"] for net in networks]
    assert "BTC" in names and "Lightning" in names
    # ETH has only disabled networks, so it should not appear
    assert "ETH" not in data

def test_kucoin_fetch_networks_data_bad_status(app, monkeypatch):
    """Test KucoinService._fetch_networks_data returns empty on HTTP status != 200."""
    service = KucoinService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse({}, status=500))
    data = service._fetch_networks_data()
    assert data == {}

def test_kucoin_fetch_networks_data_invalid_code(app, monkeypatch):
    """Test KucoinService._fetch_networks_data returns empty if API returns error code."""
    service = KucoinService()
    dummy_data = {"code": "400100", "data": []}
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_networks_data()
    assert data == {}

def test_kucoin_fetch_networks_data_error(app, monkeypatch):
    """Test KucoinService._fetch_networks_data returns empty dict on exception."""
    service = KucoinService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: (_ for _ in ()).throw(Exception("Network error")))
    data = service._fetch_networks_data()
    assert data == {}

def test_kucoin_test_connection_success(app):
    """Test KucoinService.test_connection returns True if timestamp is positive integer."""
    service = KucoinService()
    dummy_client = SimpleNamespace()
    dummy_client.get_server_timestamp = lambda: 1690000000
    service.client = dummy_client
    assert service.test_connection() is True

def test_kucoin_test_connection_failure(app):
    """Test KucoinService.test_connection returns False if client not set or API call fails."""
    service = KucoinService()
    service.client = None
    assert service.test_connection() is False
    dummy_client = SimpleNamespace()
    dummy_client.get_server_timestamp = lambda: (_ for _ in ()).throw(Exception("API failure"))
    service.client = dummy_client
    assert service.test_connection() is False

