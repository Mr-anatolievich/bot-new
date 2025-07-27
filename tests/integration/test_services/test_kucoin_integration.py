import pytest
from services.exchanges.kucoin import KucoinService

@pytest.mark.integration
def test_kucoin_trading_data_integration(app):
    """Integration test: KucoinService.get_cached_trading_data fetches real market data."""
    with app.app_context():
        app.config['KUCOIN_API_KEY'] = 'dummy'
        app.config['KUCOIN_API_SECRET'] = 'dummy'
        app.config['KUCOIN_API_PASSPHRASE'] = 'dummy'

        service = KucoinService()
        service._initialize_client()
        data = service.get_cached_trading_data()

        assert isinstance(data, dict) and data != {}, "Expected non-empty trading data"
        if data:
            sample_key = next(iter(data))
            assert sample_key.endswith("USDT"), f"Unexpected key: {sample_key}"

@pytest.mark.integration
def test_kucoin_networks_data_integration(app):
    """Integration test: KucoinService.get_cached_networks_data fetches real currency network info."""
    with app.app_context():
        service = KucoinService()
        data = service.get_cached_networks_data()

        assert isinstance(data, dict) and data != {}, "Expected non-empty network data"
        if data:
            sample_currency = next(iter(data))
            assert isinstance(data[sample_currency], list), "Expected list of networks"
