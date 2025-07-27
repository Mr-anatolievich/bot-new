import pytest
import requests
from services.exchanges.stub_services import HuobiService

class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
    def json(self):
        return self._data

def test_huobi_fetch_trading_data_success(app, monkeypatch):
    """Test HuobiService._fetch_trading_data returns data for USDT pairs only."""
    service = HuobiService()
    dummy_data = {
        "data": [
            {"symbol": "btcusdt", "bid": [101.0, 5], "ask": [102.0, 5], "close": "100.0", "vol": "1000"},
            {"symbol": "ethbtc", "bid": "0.05", "ask": "0.051", "close": "0.05", "vol": "500"},
            {"symbol": "zerousdt", "bid": 0, "ask": 1, "close": "1", "vol": "10"}
        ]
    }
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_trading_data()
    # Should include only BTCUSDT
    assert "BTCUSDT" in data and data["BTCUSDT"]["bid"] == 101.0 and data["BTCUSDT"]["ask"] == 102.0
    # Non-USDT and zero-bid pairs should be excluded
    assert "ETHBTC" not in data and "ZEROUSDT" not in data

def test_huobi_fetch_trading_data_bad_status(app, monkeypatch):
    """Test HuobiService._fetch_trading_data returns empty dict on HTTP status != 200."""
    service = HuobiService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse({}, status=500))
    data = service._fetch_trading_data()
    assert data == {}

def test_huobi_fetch_trading_data_error(app, monkeypatch):
    """Test HuobiService._fetch_trading_data returns empty dict on exception."""
    service = HuobiService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: (_ for _ in ()).throw(Exception("Network error")))
    data = service._fetch_trading_data()
    assert data == {}

def test_huobi_fetch_networks_data_success(app, monkeypatch):
    """Test HuobiService._fetch_networks_data returns all chain info grouped by currency."""
    service = HuobiService()
    dummy_data = {
        "data": [
            {
                "currency": "btc",
                "chains": [
                    {"chain": "BTC", "depositStatus": "allowed", "withdrawStatus": "prohibited", "transactFeeWithdraw": "0.001"},
                    {"chain": "Lightning", "depositStatus": "prohibited", "withdrawStatus": "prohibited", "transactFeeWithdraw": "0"}
                ]
            },
            {"currency": "eth", "chains": []}
        ]
    }
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_networks_data()
    # BTC should be included with both chains
    assert "BTC" in data and isinstance(data["BTC"], list)
    chains = [net["name"] for net in data["BTC"]]
    assert "BTC" in chains and "Lightning" in chains
    # Check deposit/withdraw booleans
    btc_main = next(net for net in data["BTC"] if net["name"] == "BTC")
    assert btc_main["deposit"] is True and btc_main["withdraw"] is False
    btc_light = next(net for net in data["BTC"] if net["name"] == "Lightning")
    assert btc_light["deposit"] is False and btc_light["withdraw"] is False
    # ETH has no chains, should not appear
    assert "ETH" not in data

def test_huobi_fetch_networks_data_bad_status(app, monkeypatch):
    """Test HuobiService._fetch_networks_data returns empty dict on HTTP status != 200."""
    service = HuobiService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse({}, status=404))
    data = service._fetch_networks_data()
    assert data == {}

def test_huobi_fetch_networks_data_error(app, monkeypatch):
    """Test HuobiService._fetch_networks_data returns empty dict on exception."""
    service = HuobiService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: (_ for _ in ()).throw(Exception("Network error")))
    data = service._fetch_networks_data()
    assert data == {}

