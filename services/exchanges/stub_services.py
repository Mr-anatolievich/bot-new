"""
Stub implementations for other exchange services
These are basic implementations to make the app work
"""
import logging
import requests
from typing import Dict, List, Any
from .base import BaseExchangeService


class GateioService(BaseExchangeService):
    """Gate.io exchange service"""

    def __init__(self):
        super().__init__('Gate.io')

    def _fetch_trading_data(self) -> Dict[str, Any]:
        try:
            response = requests.get("https://api.gateio.ws/api/v4/spot/tickers", timeout=10)
            if response.status_code != 200:
                return {}

            data = response.json()
            gateio_data = {}

            for item in data:
                symbol = item['currency_pair'].replace('_', '')
                if not symbol.endswith('USDT'):
                    continue

                bid = item.get('bid', '0')
                ask = item.get('ask', '0')

                try:
                    bid_price = float(bid)
                    ask_price = float(ask)
                    if bid_price > 0 and ask_price > 0:
                        normalized_symbol = self.normalize_symbol(symbol)
                        gateio_data[normalized_symbol] = {
                            'symbol': item['currency_pair'],
                            'bid': bid_price,
                            'ask': ask_price,
                            'last': float(item.get('last', 0)),
                            'volume': float(item.get('quote_volume', 0))
                        }
                except ValueError:
                    continue

            return gateio_data
        except Exception as e:
            self.logger.error(f"Gate.io trading data error: {e}")
            return {}

    def _fetch_networks_data(self) -> Dict[str, List[Dict]]:
        try:
            response = requests.get("https://api.gateio.ws/api/v4/wallet/currency_chains", timeout=10)
            if response.status_code != 200:
                return {}

            data = response.json()
            networks_data = {}

            for item in data:
                currency = item['currency']
                if currency not in networks_data:
                    networks_data[currency] = []

                networks_data[currency].append({
                    'name': item['chain'],
                    'deposit': item.get('is_deposit_disabled', 0) == 0,
                    'withdraw': item.get('is_withdraw_disabled', 0) == 0,
                    'fee': str(item.get('withdraw_fee', '0'))
                })

            return networks_data
        except Exception as e:
            self.logger.error(f"Gate.io networks data error: {e}")
            return {}


class HuobiService(BaseExchangeService):
    """Huobi exchange service"""

    def __init__(self):
        super().__init__('Huobi')

    def _fetch_trading_data(self) -> Dict[str, Any]:
        try:
            response = requests.get("https://api.huobi.pro/market/tickers", timeout=10)
            if response.status_code != 200:
                return {}

            data = response.json()
            huobi_data = {}

            for item in data.get('data', []):
                symbol = item['symbol'].upper()
                if not symbol.endswith('USDT'):
                    continue

                try:
                    bid = float(item['bid'][0]) if isinstance(item['bid'], list) else float(item['bid'])
                    ask = float(item['ask'][0]) if isinstance(item['ask'], list) else float(item['ask'])

                    if bid > 0 and ask > 0:
                        normalized_symbol = self.normalize_symbol(symbol)
                        huobi_data[normalized_symbol] = {
                            'symbol': item['symbol'],
                            'bid': bid,
                            'ask': ask,
                            'last': float(item.get('close', 0)),
                            'volume': float(item.get('vol', 0))
                        }
                except (ValueError, TypeError, IndexError):
                    continue

            return huobi_data
        except Exception as e:
            self.logger.error(f"Huobi trading data error: {e}")
            return {}

    def _fetch_networks_data(self) -> Dict[str, List[Dict]]:
        try:
            response = requests.get("https://api.huobi.pro/v2/reference/currencies", timeout=10)
            if response.status_code != 200:
                return {}

            data = response.json()
            networks_data = {}

            for currency in data.get('data', []):
                if 'chains' in currency and currency['chains']:
                    currency_code = currency['currency']
                    networks = []

                    for chain in currency['chains']:
                        networks.append({
                            'name': chain['chain'],
                            'deposit': chain.get('depositStatus', 'allowed') == 'allowed',
                            'withdraw': chain.get('withdrawStatus', 'allowed') == 'allowed',
                            'fee': str(chain.get('transactFeeWithdraw', '0'))
                        })

                    networks_data[currency_code] = networks

            return networks_data
        except Exception as e:
            self.logger.error(f"Huobi networks data error: {e}")
            return {}


class MexcService(BaseExchangeService):
    """MEXC exchange service"""

    def __init__(self):
        super().__init__('MEXC')

    def _fetch_trading_data(self) -> Dict[str, Any]:
        try:
            response = requests.get("https://api.mexc.com/api/v3/ticker/24hr", timeout=10)
            if response.status_code != 200:
                return {}

            data = response.json()
            mexc_data = {}

            for item in data:
                symbol = item.get('symbol', '')
                if not symbol.endswith('USDT'):
                    continue

                try:
                    bid_price = float(item.get('bidPrice', 0))
                    ask_price = float(item.get('askPrice', 0))

                    if bid_price > 0 and ask_price > 0:
                        normalized_symbol = self.normalize_symbol(symbol)
                        mexc_data[normalized_symbol] = {
                            'symbol': symbol,
                            'bid': bid_price,
                            'ask': ask_price,
                            'last': float(item.get('lastPrice', 0)),
                            'volume': float(item.get('volume', 0))
                        }
                except (ValueError, TypeError):
                    continue

            return mexc_data
        except Exception as e:
            self.logger.error(f"MEXC trading data error: {e}")
            return {}

    def _fetch_networks_data(self) -> Dict[str, List[Dict]]:
        # MEXC requires authenticated endpoint for network data
        # Return empty for now
        return {}


class BitgetService(BaseExchangeService):
    """Bitget exchange service"""

    def __init__(self):
        super().__init__('Bitget')

    def _fetch_trading_data(self) -> Dict[str, Any]:
        try:
            response = requests.get("https://api.bitget.com/api/spot/v1/market/tickers", timeout=10)
            if response.status_code != 200:
                return {}

            data = response.json()
            bitget_data = {}

            for item in data.get('data', []):
                symbol = item['symbol'].replace('_', '')
                if not symbol.endswith('USDT'):
                    continue

                try:
                    bid_price = float(item['bidPrice'])
                    ask_price = float(item['askPrice'])

                    if bid_price > 0 and ask_price > 0:
                        normalized_symbol = self.normalize_symbol(symbol)
                        bitget_data[normalized_symbol] = {
                            'symbol': item['symbol'],
                            'bid': bid_price,
                            'ask': ask_price,
                            'last': float(item.get('close', 0)),
                            'volume': float(item.get('volume', 0))
                        }
                except (ValueError, TypeError):
                    continue

            return bitget_data
        except Exception as e:
            self.logger.error(f"Bitget trading data error: {e}")
            return {}

    def _fetch_networks_data(self) -> Dict[str, List[Dict]]:
        try:
            response = requests.get("https://api.bitget.com/api/spot/v1/public/coins", timeout=10)
            if response.status_code != 200:
                return {}

            data = response.json()
            networks_data = {}

            for coin in data.get('data', []):
                if 'coinName' in coin and 'chains' in coin:
                    coin_name = coin['coinName']
                    networks = []

                    for chain in coin.get('chains', []):
                        networks.append({
                            'name': chain.get('chain', ''),
                            'deposit': chain.get('depositable', False),
                            'withdraw': chain.get('withdrawable', False),
                            'fee': str(chain.get('withdrawFee', '0'))
                        })

                    networks_data[coin_name] = networks

            return networks_data
        except Exception as e:
            self.logger.error(f"Bitget networks data error: {e}")
            return {}