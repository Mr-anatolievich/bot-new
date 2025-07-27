import pytest
from services.exchanges.stub_services import BitgetService

@pytest.mark.integration
def test_bitget_trading_data_integration(app):
    """Integration test: BitgetService.get_cached_trading_data fetches real ticker data."""
    with app.app_context():
        service = BitgetService()
        data = service.get_cached_trading_data()
        print("BITGET DATA >>>", data)
        assert isinstance(data, dict) and data != {}, "Expected non-empty dict"
        if data:
            sample_key = next(iter(data))
            assert sample_key.endswith("USDT"), f"Expected pair ending with USDT, got {sample_key}"

@pytest.mark.integration
def test_bitget_networks_data_integration(app):
    """Integration test: BitgetService.get_cached_networks_data fetches real coin network data."""
    with app.app_context():
        service = BitgetService()
        data = service.get_cached_networks_data()
        assert isinstance(data, dict) and data != {}, "Expected non-empty dict"
        if data:
            sample_coin = next(iter(data))
            assert isinstance(data[sample_coin], list), "Expected list of networks"
            assert "name" in data[sample_coin][0], "Expected 'name' key in network info"
