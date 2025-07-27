import pytest
import requests
from services.exchanges.stub_services import MexcService

class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
    def json(self):
        return self._data

def test_mexc_fetch_trading_data_success(app, monkeypatch):
    """Test MexcService._fetch_trading_data returns data for USDT trading pairs."""
    service = MexcService()
    dummy_data = [
        {"symbol": "BTCUSDT", "bidPrice": "1000", "askPrice": "1005", "lastPrice": "1002.5", "volume": "5000"},
        {"symbol": "ETHBTC", "bidPrice": "0.01", "askPrice": "0.011", "lastPrice": "0.0105", "volume": "100"},
        {"symbol": "ZEROUSDT", "bidPrice": "0", "askPrice": "1", "lastPrice": "1", "volume": "10"}
    ]
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_trading_data()
    # Should include only BTCUSDT
    assert "BTCUSDT" in data and data["BTCUSDT"]["bid"] == 1000.0 and data["BTCUSDT"]["ask"] == 1005.0
    # Non-USDT and zero-bid symbols should be filtered out
    assert "ETHBTC" not in data and "ZEROUSDT" not in data

def test_mexc_fetch_trading_data_bad_status(app, monkeypatch):
    """Test MexcService._fetch_trading_data returns empty dict on HTTP status != 200."""
    service = MexcService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse([], status=404))
    data = service._fetch_trading_data()
    assert data == {}

def test_mexc_fetch_trading_data_error(app, monkeypatch):
    """Test MexcService._fetch_trading_data returns empty dict on exception."""
    service = MexcService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: (_ for _ in ()).throw(Exception("Network error")))
    data = service._fetch_trading_data()
    assert data == {}

def test_mexc_fetch_networks_data_stub(app):
    """Test MexcService._fetch_networks_data returns empty dict (not implemented)."""
    service = MexcService()
    data = service._fetch_networks_data()
    assert data == {}

