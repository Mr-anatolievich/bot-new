"""
Binance exchange service implementation
"""
import logging
from typing import Dict, List, Any
from flask import current_app

try:
    from binance.client import Client as BinanceClient
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    BinanceClient = None

from .base import BaseExchangeService


class BinanceService(BaseExchangeService):
    """
    Binance exchange service implementation
    Handles trading data and network information from Binance API
    """

    def __init__(self):
        super().__init__('Binance')
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Binance API client"""
        if not BINANCE_AVAILABLE:
            self.logger.error("python-binance library not available")
            return

        try:
            api_key = current_app.config.get('BINANCE_API_KEY')
            api_secret = current_app.config.get('BINANCE_API_SECRET')

            if not api_key or not api_secret:
                self.logger.warning("Binance API credentials not configured")
                return

            self.client = BinanceClient(
                api_key=api_key,
                api_secret=api_secret
            )

            self.logger.info("Binance client initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Binance client: {e}")
            self.client = None

    def _fetch_trading_data(self) -> Dict[str, Any]:
        """
        Fetch trading data from Binance API
        Returns normalized trading pairs data for USDT pairs
        """
        if not self.client:
            self.logger.error("Binance client not available")
            return {}

        try:
            tickers = self.client.get_ticker()
            binance_data = {}

            for item in tickers:
                symbol = item['symbol']

                # Filter only USDT pairs
                if not symbol.endswith('USDT'):
                    continue

                # Skip if prices are zero
                bid_price = float(item.get('bidPrice', 0))
                ask_price = float(item.get('askPrice', 0))

                if bid_price <= 0 or ask_price <= 0:
                    continue

                normalized_symbol = self.normalize_symbol(symbol)

                binance_data[normalized_symbol] = {
                    'symbol': item['symbol'],
                    'bid': bid_price,
                    'ask': ask_price,
                    'last': float(item.get('lastPrice', 0)),
                    'volume': float(item.get('volume', 0)),
                    'quoteVolume': float(item.get('quoteVolume', 0)),
                    'priceChange': float(item.get('priceChange', 0)),
                    'priceChangePercent': float(item.get('priceChangePercent', 0)),
                    'count': int(item.get('count', 0))
                }

            self.logger.info(f"Fetched {len(binance_data)} trading pairs from Binance")
            return binance_data

        except Exception as e:
            self.logger.error(f"Error fetching Binance trading data: {e}")
            return {}

    def _fetch_networks_data(self) -> Dict[str, List[Dict]]:
        """
        Fetch network information from Binance API
        Returns network data for all supported coins
        """
        if not self.client:
            self.logger.error("Binance client not available")
            return {}

        try:
            coins_info = self.client.get_all_coins_info()
            networks_data = {}

            for coin_info in coins_info:
                coin = coin_info['coin']
                networks = []

                for network_info in coin_info.get('networkList', []):
                    # Parse network information
                    network = {
                        'name': network_info['network'],
                        'deposit': bool(network_info.get('depositEnable', False)),
                        'withdraw': bool(network_info.get('withdrawEnable', False)),
                        'fee': str(network_info.get('withdrawFee', '0')),
                        'min_withdraw': str(network_info.get('withdrawMin', '0')),
                        'max_withdraw': str(network_info.get('withdrawMax', '0')),
                        'confirm_times': network_info.get('minConfirm', 0),
                        'unlock_confirm': network_info.get('unLockConfirm', 0)
                    }

                    # Additional validation
                    if network['name'] and (network['deposit'] or network['withdraw']):
                        networks.append(network)

                if networks:
                    networks_data[coin] = networks

            self.logger.info(f"Fetched network data for {len(networks_data)} coins from Binance")
            return networks_data

        except Exception as e:
            self.logger.error(f"Error fetching Binance networks data: {e}")
            return {}

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information (balances, trading status)
        Useful for portfolio management features
        """
        if not self.client:
            return {}

        try:
            account = self.client.get_account()

            # Filter out zero balances
            balances = []
            for balance in account.get('balances', []):
                free = float(balance.get('free', 0))
                locked = float(balance.get('locked', 0))
                total = free + locked

                if total > 0:
                    balances.append({
                        'asset': balance['asset'],
                        'free': free,
                        'locked': locked,
                        'total': total
                    })

            return {
                'trading_status': account.get('canTrade', False),
                'withdraw_status': account.get('canWithdraw', False),
                'deposit_status': account.get('canDeposit', False),
                'balances': balances,
                'total_assets': len(balances),
                'update_time': account.get('updateTime')
            }

        except Exception as e:
            self.logger.error(f"Error fetching Binance account info: {e}")
            return {}

    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get exchange trading rules and symbol information
        """
        if not self.client:
            return {}

        try:
            info = self.client.get_exchange_info()

            # Process symbols information
            symbols_info = {}
            for symbol_info in info.get('symbols', []):
                symbol = symbol_info['symbol']

                if symbol.endswith('USDT'):
                    symbols_info[symbol] = {
                        'status': symbol_info.get('status'),
                        'base_asset': symbol_info.get('baseAsset'),
                        'quote_asset': symbol_info.get('quoteAsset'),
                        'order_types': symbol_info.get('orderTypes', []),
                        'is_spot_trading_allowed': symbol_info.get('isSpotTradingAllowed', False),
                        'filters': self._parse_symbol_filters(symbol_info.get('filters', []))
                    }

            return {
                'timezone': info.get('timezone'),
                'server_time': info.get('serverTime'),
                'symbols_count': len(symbols_info),
                'symbols': symbols_info
            }

        except Exception as e:
            self.logger.error(f"Error fetching Binance exchange info: {e}")
            return {}

    def _parse_symbol_filters(self, filters: List[Dict]) -> Dict[str, Any]:
        """Parse symbol trading filters"""
        parsed_filters = {}

        for filter_info in filters:
            filter_type = filter_info.get('filterType')

            if filter_type == 'PRICE_FILTER':
                parsed_filters['price'] = {
                    'min': float(filter_info.get('minPrice', 0)),
                    'max': float(filter_info.get('maxPrice', 0)),
                    'tick_size': float(filter_info.get('tickSize', 0))
                }

            elif filter_type == 'LOT_SIZE':
                parsed_filters['quantity'] = {
                    'min': float(filter_info.get('minQty', 0)),
                    'max': float(filter_info.get('maxQty', 0)),
                    'step_size': float(filter_info.get('stepSize', 0))
                }

            elif filter_type == 'MIN_NOTIONAL':
                parsed_filters['notional'] = {
                    'min': float(filter_info.get('minNotional', 0))
                }

        return parsed_filters

    def test_connection(self) -> bool:
        """
        Test API connection and credentials
        """
        if not self.client:
            return False

        try:
            # Test connectivity with ping
            self.client.ping()

            # Test API key with account endpoint
            account = self.client.get_account()

            if account and 'balances' in account:
                self.logger.info("Binance connection test successful")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Binance connection test failed: {e}")
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get service health status
        """
        is_connected = self.test_connection()

        status = {
            'name': self.name,
            'available': BINANCE_AVAILABLE,
            'client_initialized': self.client is not None,
            'connected': is_connected,
            'trading_cache_age': self._get_cache_age('trading'),
            'networks_cache_age': self._get_cache_age('networks'),
            'last_error': None
        }

        return status

    def _get_cache_age(self, cache_type: str) -> int:
        """Get cache age in seconds"""
        import time
        current_time = time.time()

        if cache_type == 'trading':
            return int(current_time - self._trading_cache_time)
        elif cache_type == 'networks':
            return int(current_time - self._networks_cache_time)

        return -1