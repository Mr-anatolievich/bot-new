"""
KuCoin exchange service implementation
"""
import logging
from typing import Dict, List, Any
from flask import current_app
import requests

try:
    from kucoin.client import Client as KucoinClient
    KUCOIN_AVAILABLE = True
except ImportError:
    KUCOIN_AVAILABLE = False
    KucoinClient = None

from .base import BaseExchangeService


class KucoinService(BaseExchangeService):
    """
    KuCoin exchange service implementation
    """

    def __init__(self):
        super().__init__('KuCoin')
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize KuCoin API client"""
        if not KUCOIN_AVAILABLE:
            self.logger.error("python-kucoin library not available")
            return

        try:
            api_key = current_app.config.get('KUCOIN_API_KEY')
            api_secret = current_app.config.get('KUCOIN_API_SECRET')
            api_passphrase = current_app.config.get('KUCOIN_API_PASSPHRASE')

            if not api_key or not api_secret or not api_passphrase:
                self.logger.warning("KuCoin API credentials not configured")
                return

            self.client = KucoinClient(api_key, api_secret, api_passphrase)

            self.logger.info("KuCoin client initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize KuCoin client: {e}")
            self.client = None

    def _fetch_trading_data(self) -> Dict[str, Any]:
        """Fetch trading data from KuCoin API"""
        if not self.client:
            self.logger.error("KuCoin client not available")
            return {}

        try:
            tickers = self.client.get_tickers()
            kucoin_data = {}

            if 'ticker' not in tickers:
                self.logger.error("Invalid response structure from KuCoin")
                return {}

            for item in tickers['ticker']:
                symbol = item.get('symbol', '').replace('-', '')

                if not symbol.endswith('USDT'):
                    continue

                bid = item.get('buy') or '0'
                ask = item.get('sell') or '0'

                try:
                    bid_price = float(bid)
                    ask_price = float(ask)
                except ValueError:
                    continue

                if bid_price <= 0 or ask_price <= 0:
                    continue

                normalized_symbol = self.normalize_symbol(symbol)

                kucoin_data[normalized_symbol] = {
                    'symbol': item.get('symbol', ''),
                    'bid': bid_price,
                    'ask': ask_price,
                    'last': float(item.get('last', 0)),
                    'volume': float(item.get('vol', 0)),
                    'volValue': float(item.get('volValue', 0)),
                    'priceChangePercent': float(item.get('changeRate', 0)) * 100,
                    'high24h': float(item.get('high', 0)),
                    'low24h': float(item.get('low', 0))
                }

            self.logger.info(f"Fetched {len(kucoin_data)} trading pairs from KuCoin")
            return kucoin_data

        except Exception as e:
            self.logger.error(f"Error fetching KuCoin trading data: {e}")
            return {}

    def _fetch_networks_data(self) -> Dict[str, List[Dict]]:
        """Fetch network information from KuCoin API"""
        try:
            # Use public endpoint for currencies
            response = requests.get("https://api.kucoin.com/api/v3/currencies", timeout=10)

            if response.status_code != 200:
                self.logger.error(f"KuCoin networks API returned status {response.status_code}")
                return {}

            data = response.json()
            networks_data = {}

            if data.get('code') != '200000' or 'data' not in data:
                self.logger.error("Invalid response from KuCoin currencies API")
                return {}

            coins_data = data.get('data', [])
            if not coins_data:
                return {}

            for coin in coins_data:
                if 'currency' not in coin or 'chains' not in coin:
                    continue

                currency = coin['currency']
                chains = coin.get('chains', [])

                if not chains:
                    continue

                networks = []
                for chain in chains:
                    if 'chainName' not in chain:
                        continue

                    network = {
                        'name': chain['chainName'],
                        'deposit': chain.get('isDepositEnabled', False),
                        'withdraw': chain.get('isWithdrawEnabled', False),
                        'fee': str(chain.get('withdrawalMinFee', '0')),
                        'min_withdraw': str(chain.get('withdrawalMinSize', '0')),
                        'confirm_times': int(chain.get('confirms', 0))
                    }

                    if network['name'] and (network['deposit'] or network['withdraw']):
                        networks.append(network)

                if networks:
                    networks_data[currency] = networks

            self.logger.info(f"Fetched network data for {len(networks_data)} coins from KuCoin")
            return networks_data

        except Exception as e:
            self.logger.error(f"Error fetching KuCoin networks data: {e}")
            return {}

    def test_connection(self) -> bool:
        """Test API connection"""
        if not self.client:
            return False

        try:
            result = self.client.get_server_timestamp()
            return isinstance(result, int) and result > 0

        except Exception as e:
            self.logger.error(f"KuCoin connection test failed: {e}")
            return False