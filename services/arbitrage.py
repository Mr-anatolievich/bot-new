"""
Arbitrage calculation and analysis service
"""
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from flask import current_app

from .exchanges.base import get_exchange_manager, BaseExchangeService


class ArbitrageService:
    """
    Service for calculating and analyzing arbitrage opportunities
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchange_manager = get_exchange_manager()

    def find_arbitrage_opportunities(
            self,
            min_spread: float = None,
            exchange_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find arbitrage opportunities between exchanges

        Args:
            min_spread: Minimum profit spread percentage (default from config)
            exchange_filter: Filter by specific exchange name

        Returns:
            List of arbitrage opportunities sorted by spread (descending)
        """
        if min_spread is None:
            min_spread = current_app.config.get('MIN_ARBITRAGE_SPREAD', 0.1)

        # Get data from all exchanges
        exchange_data = self._get_filtered_exchange_data(exchange_filter)

        if len(exchange_data) < 2:
            self.logger.warning("Need at least 2 exchanges for arbitrage calculation")
            return []

        # Count symbols across exchanges
        symbol_counts = defaultdict(int)
        for data in exchange_data.values():
            for symbol in data.keys():
                if BaseExchangeService.is_stablecoin_pair(symbol):
                    symbol_counts[symbol] += 1

        # Only symbols present on at least 2 exchanges
        common_symbols = [s for s, count in symbol_counts.items() if count >= 2]

        opportunities = []
        for symbol in common_symbols:
            opportunity = self._calculate_arbitrage_for_symbol(
                symbol, exchange_data, min_spread
            )
            if opportunity:
                opportunities.append(opportunity)

        return sorted(opportunities, key=lambda x: x['spread'], reverse=True)

    def _get_filtered_exchange_data(self, exchange_filter: Optional[str]) -> Dict[str, Dict]:
        """Get trading data from exchanges with optional filtering"""
        all_data = self.exchange_manager.get_all_trading_data()

        if exchange_filter:
            # Filter by specific exchange
            filtered_data = {}
            for name, data in all_data.items():
                if exchange_filter.lower() in name.lower():
                    filtered_data[name] = data
            return filtered_data

        return all_data

    def _calculate_arbitrage_for_symbol(
            self,
            symbol: str,
            exchange_data: Dict[str, Dict],
            min_spread: float
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate arbitrage opportunity for a specific symbol
        """
        prices = {}

        # Collect prices from exchanges that have this symbol
        for exchange, data in exchange_data.items():
            if symbol in data and data[symbol].get('ask', 0) > 0:
                prices[exchange] = {
                    'bid': data[symbol].get('bid', 0),
                    'ask': data[symbol].get('ask', 0),
                    'volume': data[symbol].get('volume', 0)
                }

        if len(prices) < 2:
            return None

        # Find best buy (lowest ask) and sell (highest bid) exchanges
        best_ask = min(prices.items(), key=lambda x: x[1]['ask'])
        best_bid = max(prices.items(), key=lambda x: x[1]['bid'])

        # Skip if same exchange
        if best_ask[0] == best_bid[0]:
            return None

        # Calculate spread percentage
        buy_price = best_ask[1]['ask']
        sell_price = best_bid[1]['bid']
        spread_percent = ((sell_price - buy_price) / buy_price) * 100

        if spread_percent < min_spread:
            return None

        # Get network information
        networks = self._get_networks_for_symbol(symbol)

        return {
            'symbol': symbol,
            'buy_exchange': best_ask[0],
            'buy_price': buy_price,
            'sell_exchange': best_bid[0],
            'sell_price': sell_price,
            'spread': spread_percent,
            'profit': sell_price - buy_price,
            'volume': best_ask[1]['volume'],
            'networks': networks
        }

    def _get_networks_for_symbol(self, symbol: str) -> List[Dict[str, str]]:
        """
        Get available networks for a token across all exchanges
        """
        base_token = BaseExchangeService.get_base_token(symbol)
        networks_by_exchange = {}

        for exchange_name, exchange_service in self.exchange_manager.get_all_exchanges().items():
            try:
                networks_data = exchange_service.get_cached_networks_data()
                if base_token in networks_data:
                    networks = networks_data[base_token]
                    if networks:
                        net_names = ', '.join(sorted({net['name'] for net in networks}))
                        networks_by_exchange[exchange_name] = net_names
            except Exception as e:
                self.logger.error(f"Failed to get networks from {exchange_name}: {e}")

        # Format result
        result = []
        for exchange, networks in networks_by_exchange.items():
            result.append({
                'exchange': exchange,
                'networks': networks
            })

        return result

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get dashboard statistics for display
        """
        try:
            # Get current arbitrage opportunities
            opportunities = self.find_arbitrage_opportunities(min_spread=0.05)

            # Calculate stats
            total_opportunities = len(opportunities)
            profitable_opportunities = len([op for op in opportunities if op['spread'] > 0.1])

            # Mock profit calculation (in real app, get from database)
            estimated_profit_24h = sum(op.get('profit', 0) * 100 for op in opportunities[:10])

            # Get active exchanges count
            active_exchanges = len(self.exchange_manager.get_exchange_names())

            # Calculate success rate (mock data)
            success_rate = 96.2

            stats = [
                {
                    'title': 'Total Profit (24h)',
                    'value': f'${estimated_profit_24h:.2f}',
                    'change': '+5.4%',
                    'icon': 'fas fa-wallet',
                    'color': 'primary',
                    'changeColor': 'text-green-600 dark:text-green-400'
                },
                {
                    'title': 'Active Opportunities',
                    'value': str(total_opportunities),
                    'change': '+12.7%',
                    'icon': 'fas fa-chart-pie',
                    'color': 'secondary',
                    'changeColor': 'text-green-600 dark:text-green-400'
                },
                {
                    'title': 'Profitable (>0.1%)',
                    'value': str(profitable_opportunities),
                    'change': '+8.3%',
                    'icon': 'fas fa-chart-line',
                    'color': 'warning',
                    'changeColor': 'text-green-600 dark:text-green-400'
                },
                {
                    'title': 'Active Exchanges',
                    'value': str(active_exchanges),
                    'change': '0%',
                    'icon': 'fas fa-exchange-alt',
                    'color': 'primary',
                    'changeColor': 'text-gray-600 dark:text-gray-400'
                }
            ]

            # Generate top tokens by profit potential
            top_tokens = self._get_top_tokens(opportunities[:10])

            # Mock recent trades (in real app, get from database)
            recent_trades = [
                {
                    'id': '1',
                    'token': 'BTC/USDT',
                    'tokenName': 'Bitcoin',
                    'tokenSymbol': 'BTC',
                    'exchanges': 'Binance → KuCoin',
                    'profit': '+$124.50 (1.2%)',
                    'time': '2 minutes ago',
                    'success': True
                },
                {
                    'id': '2',
                    'token': 'ETH/USDT',
                    'tokenName': 'Ethereum',
                    'tokenSymbol': 'ETH',
                    'exchanges': 'Bybit → MEXC',
                    'profit': '+$87.30 (0.8%)',
                    'time': '15 minutes ago',
                    'success': True
                },
                {
                    'id': '3',
                    'token': 'SOL/USDT',
                    'tokenName': 'Solana',
                    'tokenSymbol': 'SOL',
                    'exchanges': 'Gate.io → Huobi',
                    'profit': 'Failed',
                    'time': '32 minutes ago',
                    'success': False
                }
            ]

            return {
                'stats': stats,
                'recent_trades': recent_trades,
                'top_tokens': top_tokens
            }

        except Exception as e:
            self.logger.error(f"Failed to get dashboard stats: {e}")
            return {'stats': [], 'recent_trades': [], 'top_tokens': []}

    def _get_top_tokens(self, opportunities: List[Dict]) -> List[Dict[str, str]]:
        """Get top performing tokens from opportunities"""
        token_profits = {}

        for opp in opportunities:
            symbol = opp.get('symbol', '').replace('USDT', '')
            if symbol:
                if symbol not in token_profits:
                    token_profits[symbol] = {'count': 0, 'total_profit': 0}
                token_profits[symbol]['count'] += 1
                token_profits[symbol]['total_profit'] += opp.get('profit', 0)

        # Sort by total profit and take top 4
        sorted_tokens = sorted(
            token_profits.items(),
            key=lambda x: x[1]['total_profit'],
            reverse=True
        )[:4]

        top_tokens = []
        for symbol, data in sorted_tokens:
            avg_profit = data['total_profit'] / max(data['count'], 1)
            top_tokens.append({
                'name': symbol,
                'symbol': symbol,
                'profit': f"+${data['total_profit']:.2f}",
                'avgProfit': f"{avg_profit:.1f}%"
            })

        return top_tokens

    def get_table_data(self) -> List[Dict[str, Any]]:
        """
        Get formatted table data for arbitrage opportunities display
        """
        opportunities = self.find_arbitrage_opportunities()

        table = []
        for opp in opportunities:
            # Format networks for display
            networks = []
            for net_info in opp.get('networks', []):
                networks.append({
                    'exchange': net_info['exchange'],
                    'label': net_info['networks']
                })

            table.append({
                "pair": opp['symbol'],
                "buy_price": opp['buy_price'],
                "buy_exchange": opp['buy_exchange'],
                "sell_price": opp['sell_price'],
                "sell_exchange": opp['sell_exchange'],
                "spread": opp['spread'],
                "networks": networks
            })

        return table

    def format_opportunities_for_api(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Format arbitrage opportunities for API response
        """
        formatted = []

        for opp in opportunities:
            formatted.append({
                'id': f"{opp['symbol']}_{opp['buy_exchange']}_{opp['sell_exchange']}",
                'token': opp['symbol'].replace('USDT', ''),
                'symbol': opp['symbol'],
                'tokenSymbol': opp['symbol'].replace('USDT', ''),
                'buyExchange': opp['buy_exchange'],
                'buyPrice': f"${opp['buy_price']:.6f}",
                'sellExchange': opp['sell_exchange'],
                'sellPrice': f"${opp['sell_price']:.6f}",
                'spread': f"{opp['spread']:.2f}%",
                'volume': f"${opp.get('volume', 0):,.0f}",
                'estProfit': f"${opp['profit']:.2f}",
                'networks': [{'name': net['networks']} for net in opp.get('networks', [])]
            })

        return formatted