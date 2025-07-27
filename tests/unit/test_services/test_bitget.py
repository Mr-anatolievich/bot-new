import pytest
import requests
from services.exchanges.stub_services import BitgetService

class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
    def json(self):
        return self._data

def test_bitget_fetch_trading_data_success(app, monkeypatch):
    """Test BitgetService._fetch_trading_data returns filtered USDT pairs data."""
    service = BitgetService()
    dummy_data = {
        "data": [
            {"symbol": "BTC_USDT", "bidPrice": "500.0", "askPrice": "505.0", "close": "502.5", "volume": "10000"},
            {"symbol": "ETH_BTC", "bidPrice": "0.02", "askPrice": "0.021", "close": "0.0205", "volume": "200"},
            {"symbol": "ZERO_USDT", "bidPrice": "0", "askPrice": "1", "close": "1", "volume": "50"}
        ]
    }
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_trading_data()
    # Only BTCUSDT should be included
    assert "BTCUSDT" in data and data["BTCUSDT"]["bid"] == 500.0 and data["BTCUSDT"]["ask"] == 505.0
    # Non-USDT and zero-bid symbols should be filtered out
    assert "ETHBTC" not in data and "ZEROUSDT" not in data

def test_bitget_fetch_trading_data_bad_status(app, monkeypatch):
    """Test BitgetService._fetch_trading_data returns empty dict on HTTP status != 200."""
    service = BitgetService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse({"data": []}, status=503))
    data = service._fetch_trading_data()
    assert data == {}

def test_bitget_fetch_trading_data_error(app, monkeypatch):
    """Test BitgetService._fetch_trading_data returns empty dict on exception."""
    service = BitgetService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: (_ for _ in ()).throw(Exception("Network error")))
    data = service._fetch_trading_data()
    assert data == {}

def test_bitget_fetch_networks_data_success(app, monkeypatch):
    """Test BitgetService._fetch_networks_data returns all chains grouped by coin."""
    service = BitgetService()
    dummy_data = {
        "data": [
            {
                "coinName": "BTC",
                "chains": [
                    {"chain": "BTC", "depositable": True, "withdrawable": False, "withdrawFee": "0.001"},
                    {"chain": "Lightning", "depositable": False, "withdrawable": False, "withdrawFee": "0"}
                ]
            },
            {"coinName": "ETH", "chains": []},
            {"foo": "bar"}
        ]
    }
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_networks_data()
    # BTC should be included with both chains
    assert "BTC" in data and isinstance(data["BTC"], list)
    net_names = [net["name"] for net in data["BTC"]]
    assert "BTC" in net_names and "Lightning" in net_names
    # Check deposit/withdraw flags
    btc_main = next(net for net in data["BTC"] if net["name"] == "BTC")
    assert btc_main["deposit"] is True and btc_main["withdraw"] is False
    btc_light = next(net for net in data["BTC"] if net["name"] == "Lightning")
    assert btc_light["deposit"] is False and btc_light["withdraw"] is False
    # ETH should appear with empty list of networks
    assert "ETH" in data and data["ETH"] == []
    # Entry without coinName should be skipped
    assert "bar" not in data

def test_bitget_fetch_networks_data_bad_status(app, monkeypatch):
    """Test BitgetService._fetch_networks_data returns empty dict on HTTP status != 200."""
    service = BitgetService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse({}, status=400))
    data = service._fetch_networks_data()
    assert data == {}

def test_bitget_fetch_networks_data_error(app, monkeypatch):
    """Test BitgetService._fetch_networks_data returns empty dict on exception."""
    service = BitgetService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: (_ for _ in ()).throw(Exception("Network error")))
    data = service._fetch_networks_data()
    assert data == {}

