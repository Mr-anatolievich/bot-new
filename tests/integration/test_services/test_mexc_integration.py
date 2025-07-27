import pytest
from services.exchanges.stub_services import MexcService

@pytest.mark.integration
def test_mexc_trading_data_integration(app):
    """Integration test: MexcService.get_cached_trading_data fetches real market data."""
    with app.app_context():
        service = MexcService()
        data = service.get_cached_trading_data()

        assert isinstance(data, dict) and data != {}, "Expected non-empty trading data"
        if data:
            sample_key = next(iter(data))
            assert sample_key.endswith("USDT"), f"Unexpected key: {sample_key}"
