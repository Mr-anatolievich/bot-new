import pytest
from services.exchanges.binance import BinanceService

@pytest.mark.integration
def test_binance_trading_data_integration(app):
    """Integration test: BinanceService.get_cached_trading_data fetches real market data (public API)."""
    with app.app_context():
        # Set dummy config inside app context
        app.config['BINANCE_API_KEY'] = 'dummy'
        app.config['BINANCE_API_SECRET'] = 'dummy'

        service = BinanceService()
        service._initialize_client()  # Optional for public endpoints

        data = service.get_cached_trading_data()
        assert isinstance(data, dict), "Expected dict of trading data"
        assert data != {}, "Trading data should not be empty"

        sample_key = next(iter(data))
        assert sample_key.endswith("USDT"), f"Unexpected symbol: {sample_key}"
