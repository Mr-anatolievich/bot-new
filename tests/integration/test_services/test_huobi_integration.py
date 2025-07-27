import pytest
from services.exchanges.stub_services import HuobiService

@pytest.mark.integration
def test_huobi_trading_data_integration(app):
    """Integration test: HuobiService.get_cached_trading_data fetches real market data."""
    with app.app_context():
        service = HuobiService()
        data = service.get_cached_trading_data()
        assert isinstance(data, dict) and data != {}, "Expected non-empty trading data"
        if data:
            sample_key = next(iter(data))
            assert sample_key.endswith("USDT"), f"Expected key ending with USDT, got {sample_key}"

@pytest.mark.integration
def test_huobi_networks_data_integration(app):
    """Integration test: HuobiService.get_cached_networks_data fetches real currency networks."""
    with app.app_context():
        service = HuobiService()
        data = service.get_cached_networks_data()
        assert isinstance(data, dict) and data != {}, "Expected non-empty networks data"
        if data:
            sample_currency = next(iter(data))
            assert isinstance(data[sample_currency], list), "Expected list of networks"
            assert "name" in data[sample_currency][0], "Missing 'name' field in network info"
