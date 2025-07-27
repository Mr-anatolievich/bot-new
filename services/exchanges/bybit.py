"""
Bybit exchange service implementation
"""
import logging
from typing import Dict, List, Any
from flask import current_app

try:
    from pybit.unified_trading import HTTP as BybitClient
    BYBIT_AVAILABLE = True
except ImportError:
    BYBIT_AVAILABLE = False
    BybitClient = None

from .base import BaseExchangeService


class BybitService(BaseExchangeService):
    """
    Bybit exchange service implementation
    """

    def __init__(self):
        super().__init__('Bybit')
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Bybit API client"""
        if not BYBIT_AVAILABLE:
            self.logger.error("pybit library not available")
            return

        try:
            api_key = current_app.config.get('BYBIT_API_KEY')
            api_secret = current_app.config.get('BYBIT_API_SECRET')

            if not api_key or not api_secret:
                self.logger.warning("Bybit API credentials not configured")
                return

            self.client = BybitClient(
                api_key=api_key,
                api_secret=api_secret,
                testnet=False
            )

            self.logger.info("Bybit client initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Bybit client: {e}")
            self.client = None

    def _fetch_trading_data(self) -> Dict[str, Any]:
        """Fetch trading data from Bybit API"""
        if not self.client:
            self.logger.error("Bybit client not available")
            return {}

        try:
            result = self.client.get_tickers(category='spot')
            bybit_data = {}

            if 'result' not in result or 'list' not in result['result']:
                self.logger.error("Invalid response structure from Bybit")
                return {}

            for item in result['result']['list']:
                symbol = item['symbol']

                if not symbol.endswith('USDT'):
                    continue

                bid_price = float(item.get('bid1Price', 0))
                ask_price = float(item.get('ask1Price', 0))

                if bid_price <= 0 or ask_price <= 0:
                    continue

                normalized_symbol = self.normalize_symbol(symbol)

                bybit_data[normalized_symbol] = {
                    'symbol': item['symbol'],
                    'bid': bid_price,
                    'ask': ask_price,
                    'last': float(item.get('lastPrice', 0)),
                    'volume': float(item.get('volume24h', 0)),
                    'turnover24h': float(item.get('turnover24h', 0)),
                    'priceChangePercent': float(item.get('price24hPcnt', 0)) * 100,
                    'highPrice24h': float(item.get('highPrice24h', 0)),
                    'lowPrice24h': float(item.get('lowPrice24h', 0))
                }

            self.logger.info(f"Fetched {len(bybit_data)} trading pairs from Bybit")
            return bybit_data

        except Exception as e:
            self.logger.error(f"Error fetching Bybit trading data: {e}")
            return {}

    def _fetch_networks_data(self) -> Dict[str, List[Dict]]:
        """Fetch network information from Bybit API"""
        if not self.client:
            self.logger.error("Bybit client not available")
            return {}

        try:
            result = self.client.get_coin_info()
            networks_data = {}

            if 'result' not in result or 'rows' not in result['result']:
                self.logger.error("Invalid response structure from Bybit networks")
                return {}

            for row in result['result']['rows']:
                coin = row['coin']
                networks = []

                for chain in row.get('chains', []):
                    network = {
                        'name': chain['chain'],
                        'deposit': chain.get('chainDeposit') == '1',
                        'withdraw': chain.get('chainWithdraw') == '1',
                        'fee': str(chain.get('withdrawFee', '0')),
                        'min_withdraw': str(chain.get('withdrawMinSize', '0')),
                        'confirm_times': int(chain.get('confirmTimes', 0))
                    }

                    if network['name'] and (network['deposit'] or network['withdraw']):
                        networks.append(network)

                if networks:
                    networks_data[coin] = networks

            self.logger.info(f"Fetched network data for {len(networks_data)} coins from Bybit")
            return networks_data

        except Exception as e:
            self.logger.error(f"Error fetching Bybit networks data: {e}")
            return {}

    def test_connection(self) -> bool:
        """Test API connection"""
        if not self.client:
            return False

        try:
            result = self.client.get_server_time()
            return 'result' in result and 'timeSecond' in result['result']

        except Exception as e:
            self.logger.error(f"Bybit connection test failed: {e}")
            return False