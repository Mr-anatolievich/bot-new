"""
Base exchange service class and utilities
"""
import time
import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from flask import current_app


class BaseExchangeService(ABC):
    """
    Base class for all exchange services
    Provides common functionality for data fetching, caching, and normalization
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Cache variables
        self._trading_data_cache = {}
        self._networks_data_cache = {}
        self._trading_cache_time = 0
        self._networks_cache_time = 0
        self._cache_duration = current_app.config.get('CACHE_DURATION', 3600)

    @abstractmethod
    def _fetch_trading_data(self) -> Dict[str, Any]:
        """
        Fetch raw trading data from exchange API
        Must be implemented by each exchange service
        """
        pass

    @abstractmethod
    def _fetch_networks_data(self) -> Dict[str, List[Dict]]:
        """
        Fetch raw networks data from exchange API
        Must be implemented by each exchange service
        """
        pass

    def get_cached_trading_data(self) -> Dict[str, Any]:
        """
        Get trading data with caching
        Returns normalized trading data for USDT pairs
        """
        current_time = time.time()

        if current_time - self._trading_cache_time > self._cache_duration:
            try:
                self._trading_data_cache = self._fetch_trading_data()
                self._trading_cache_time = current_time
                self.logger.info(f"Updated trading data cache for {self.name}")
            except Exception as e:
                self.logger.error(f"Failed to fetch trading data from {self.name}: {e}")
                return {}

        return self._trading_data_cache

    def get_cached_networks_data(self) -> Dict[str, List[Dict]]:
        """
        Get networks data with caching
        Returns network information for tokens
        """
        current_time = time.time()

        if current_time - self._networks_cache_time > self._cache_duration:
            try:
                self._networks_data_cache = self._fetch_networks_data()
                self._networks_cache_time = current_time
                self.logger.info(f"Updated networks data cache for {self.name}")
            except Exception as e:
                self.logger.error(f"Failed to fetch networks data from {self.name}: {e}")
                return {}

        return self._networks_data_cache

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """
        Normalize trading pair symbol
        Removes special characters and standardizes format
        """
        symbol = symbol.replace('-', '').replace('_', '').replace('/', '').upper()
        if symbol.endswith(('USDT', 'USDC')):
            return symbol[:-4] + symbol[-4:]
        return symbol

    @staticmethod
    def get_base_token(symbol: str) -> str:
        """
        Extract base token from trading pair symbol
        E.g., 'BTCUSDT' -> 'BTC'
        """
        match = re.match(r'^([A-Z]+)(USDT|BTC|ETH|BUSD|USDC)$', symbol)
        return match.group(1) if match else symbol

    @staticmethod
    def is_stablecoin_pair(symbol: str) -> bool:
        """
        Check if trading pair is a stablecoin pair
        """
        return symbol.endswith('USDT')

    def format_token_data(self, raw_data: Dict) -> List[Dict]:
        """
        Format raw token data for display
        """
        tokens = []
        networks_data = self.get_cached_networks_data()

        for symbol, data in raw_data.items():
            base_token = self.get_base_token(symbol)
            token_networks = []

            # Get networks for this token
            if base_token in networks_data:
                for net in networks_data[base_token]:
                    fee = net.get('fee', '0')
                    label = f"{net['name']}"
                    if fee and fee != '0':
                        label += f" ({fee} USDT)" if net['name'] != "DGB" else f" ({fee})"

                    token_networks.append({
                        'name': net['name'],
                        'label': label
                    })

            # Calculate internal spread
            spread = 0
            if data.get('ask', 0) > 0:
                spread = ((data.get('bid', 0) - data['ask']) / data['ask']) * 100

            tokens.append({
                'symbol': symbol,
                'bid': data.get('bid', 0),
                'ask': data.get('ask', 0),
                'last': data.get('last', 0),
                'volume': data.get('volume', 0),
                'spread': spread,
                'networks': token_networks
            })

        return sorted(tokens, key=lambda x: x['symbol'])

    def clear_cache(self):
        """Clear all cached data"""
        self._trading_data_cache = {}
        self._networks_data_cache = {}
        self._trading_cache_time = 0
        self._networks_cache_time = 0
        self.logger.info(f"Cleared cache for {self.name}")


class ExchangeManager:
    """
    Manager class for all exchange services
    Provides unified interface for accessing multiple exchanges
    """

    def __init__(self):
        self._exchanges = {}
        self.logger = logging.getLogger(__name__)

    def register_exchange(self, exchange_service: BaseExchangeService):
        """Register an exchange service"""
        self._exchanges[exchange_service.name] = exchange_service
        self.logger.info(f"Registered exchange: {exchange_service.name}")

    def get_exchange(self, name: str) -> Optional[BaseExchangeService]:
        """Get exchange service by name"""
        return self._exchanges.get(name)

    def get_all_exchanges(self) -> Dict[str, BaseExchangeService]:
        """Get all registered exchanges"""
        return self._exchanges.copy()

    def get_exchange_names(self) -> List[str]:
        """Get list of registered exchange names"""
        return list(self._exchanges.keys())

    def get_all_trading_data(self) -> Dict[str, Dict]:
        """Get trading data from all exchanges"""
        data = {}
        for name, exchange in self._exchanges.items():
            try:
                data[name] = exchange.get_cached_trading_data()
            except Exception as e:
                self.logger.error(f"Failed to get trading data from {name}: {e}")
                data[name] = {}
        return data

    def get_all_networks_data(self) -> Dict[str, Dict]:
        """Get networks data from all exchanges"""
        data = {}
        for name, exchange in self._exchanges.items():
            try:
                data[name] = exchange.get_cached_networks_data()
            except Exception as e:
                self.logger.error(f"Failed to get networks data from {name}: {e}")
                data[name] = {}
        return data

    def clear_all_caches(self):
        """Clear cache for all exchanges"""
        for exchange in self._exchanges.values():
            exchange.clear_cache()
        self.logger.info("Cleared cache for all exchanges")


# Global exchange manager instance
exchange_manager = ExchangeManager()


def get_exchange_manager() -> ExchangeManager:
    """Get the global exchange manager instance"""
    return exchange_manager


def register_all_exchanges():
    """
    Register all available exchange services
    This function should be called during app initialization
    """
    try:
        # Import and register exchange services
        from .binance import BinanceService
        from .bybit import BybitService
        from .kucoin import KucoinService
        from .stub_services import GateioService, HuobiService, MexcService, BitgetService

        # Register exchanges
        exchange_manager.register_exchange(BinanceService())
        exchange_manager.register_exchange(BybitService())
        exchange_manager.register_exchange(KucoinService())
        exchange_manager.register_exchange(GateioService())
        exchange_manager.register_exchange(HuobiService())
        exchange_manager.register_exchange(MexcService())
        exchange_manager.register_exchange(BitgetService())

        logging.info("All exchange services registered successfully")

    except ImportError as e:
        logging.warning(f"Some exchange services not available: {e}")