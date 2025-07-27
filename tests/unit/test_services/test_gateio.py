import pytest
import requests
from services.exchanges.stub_services import GateioService

class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
    def json(self):
        return self._data

def test_gateio_fetch_trading_data_success(app, monkeypatch):
    """Test GateioService._fetch_trading_data returns filtered data for USDT pairs."""
    service = GateioService()
    dummy_data = [
        {"currency_pair": "BTC_USDT", "bid": "100.0", "ask": "101.0", "last": "100.5", "quote_volume": "1000"},
        {"currency_pair": "ETH_BTC", "bid": "10", "ask": "11", "last": "10.5", "quote_volume": "500"},
        {"currency_pair": "ZERO_USDT", "bid": "0", "ask": "1", "last": "1", "quote_volume": "10"}
    ]
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_trading_data()
    # Only BTCUSDT should be included
    assert isinstance(data, dict)
    assert "BTCUSDT" in data and data["BTCUSDT"]["bid"] == 100.0 and data["BTCUSDT"]["ask"] == 101.0
    # Non-USDT and zero-bid entries should be filtered out
    assert "ETHBTC" not in data and "ZEROUSDT" not in data

def test_gateio_fetch_trading_data_bad_status(app, monkeypatch):
    """Test GateioService._fetch_trading_data returns empty dict on HTTP status != 200."""
    service = GateioService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse([], status=404))
    data = service._fetch_trading_data()
    assert data == {}

def test_gateio_fetch_trading_data_error(app, monkeypatch):
    """Test GateioService._fetch_trading_data returns empty dict on request exception."""
    service = GateioService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: (_ for _ in ()).throw(Exception("Network error")))
    data = service._fetch_trading_data()
    assert data == {}

def test_gateio_fetch_networks_data_success(app, monkeypatch):
    """Test GateioService._fetch_networks_data returns all networks grouped by currency."""
    service = GateioService()
    dummy_data = [
        {"currency": "BTC", "chain": "BTC", "is_deposit_disabled": 0, "is_withdraw_disabled": 1, "withdraw_fee": "0.001"},
        {"currency": "BTC", "chain": "Lightning", "is_deposit_disabled": 1, "is_withdraw_disabled": 1, "withdraw_fee": "0.0001"},
        {"currency": "ETH", "chain": "ETH", "is_deposit_disabled": 0, "is_withdraw_disabled": 0, "withdraw_fee": "0.01"}
    ]
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse(dummy_data))
    data = service._fetch_networks_data()
    # Should group networks by currency
    assert "BTC" in data and "ETH" in data
    # BTC should have both networks listed
    assert any(net["name"] == "BTC" for net in data["BTC"])
    assert any(net["name"] == "Lightning" for net in data["BTC"])
    # Check boolean conversion for deposit/withdraw flags
    btc_net0 = next(net for net in data["BTC"] if net["name"] == "BTC")
    assert btc_net0["deposit"] is True and btc_net0["withdraw"] is False
    btc_net1 = next(net for net in data["BTC"] if net["name"] == "Lightning")
    assert btc_net1["deposit"] is False and btc_net1["withdraw"] is False
    # ETH network should be present with deposit and withdraw True
    eth_net = data["ETH"][0]
    assert eth_net["deposit"] is True and eth_net["withdraw"] is True

def test_gateio_fetch_networks_data_bad_status(app, monkeypatch):
    """Test GateioService._fetch_networks_data returns empty dict on HTTP status != 200."""
    service = GateioService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: DummyResponse([], status=500))
    data = service._fetch_networks_data()
    assert data == {}

def test_gateio_fetch_networks_data_error(app, monkeypatch):
    """Test GateioService._fetch_networks_data returns empty dict on exception."""
    service = GateioService()
    monkeypatch.setattr(requests, "get", lambda url, timeout=10: (_ for _ in ()).throw(Exception("Network error")))
    data = service._fetch_networks_data()
    assert data == {}

