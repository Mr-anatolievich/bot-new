import pytest
from services.exchanges.bybit import BybitService

@pytest.mark.integration
def test_bybit_trading_data_integration(app):
    """Integration test: BybitService.get_cached_trading_data fetches real market data."""
    with app.app_context():
        app.config['BYBIT_API_KEY'] = 'dummy'
        app.config['BYBIT_API_SECRET'] = 'dummy'

        service = BybitService()
        service._initialize_client()

        data = service.get_cached_trading_data()
        assert isinstance(data, dict) and data != {}, "Expected non-empty dict of trading data"
        if data:
            sample_key = next(iter(data))
            assert sample_key.endswith("USDT"), f"Expected pair ending with USDT, got {sample_key}"
