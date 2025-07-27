"""
Arbitrage API routes
"""

from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

from services import ArbitrageService, get_all_exchange_services

# Create blueprint
arbitrage_bp = Blueprint('arbitrage', __name__)
logger = logging.getLogger(__name__)

# Initialize services
arbitrage_service = ArbitrageService()


@arbitrage_bp.route('/dashboard')
def api_dashboard():
    """
    API endpoint for Dashboard data
    Returns stats, recent trades, and top tokens
    """
    try:
        dashboard_data = arbitrage_service.get_dashboard_stats()

        return jsonify({
            'status': 'success',
            'data': dashboard_data
        })

    except Exception as e:
        logger.error(f"Dashboard API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load dashboard data'
        }), 500


@arbitrage_bp.route('/arbitrage')
def api_arbitrage():
    """
    API endpoint for arbitrage opportunities
    Supports filtering by min_spread and exchange
    """
    try:
        # Get query parameters
        min_spread = request.args.get('min_spread', 0.1, type=float)
        exchange_filter = request.args.get('exchange', None)
        limit = request.args.get('limit', 50, type=int)

        # Validate parameters
        if min_spread < 0 or min_spread > 100:
            return jsonify({
                'status': 'error',
                'message': 'min_spread must be between 0 and 100'
            }), 400

        if limit < 1 or limit > 1000:
            return jsonify({
                'status': 'error',
                'message': 'limit must be between 1 and 1000'
            }), 400

        # Get arbitrage opportunities
        opportunities = arbitrage_service.find_arbitrage_opportunities(
            min_spread=min_spread,
            exchange_filter=exchange_filter
        )

        # Apply limit
        limited_opportunities = opportunities[:limit]

        # Format for React UI
        formatted_opportunities = arbitrage_service.format_opportunities_for_api(
            limited_opportunities
        )

        return jsonify({
            'status': 'success',
            'data': {
                'opportunities': formatted_opportunities,
                'total': len(opportunities),
                'returned': len(limited_opportunities),
                'filters': {
                    'min_spread': min_spread,
                    'exchange': exchange_filter,
                    'limit': limit
                }
            }
        })

    except Exception as e:
        logger.error(f"Arbitrage API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load arbitrage opportunities'
        }), 500


@arbitrage_bp.route('/arbitrage/stats')
def api_arbitrage_stats():
    """
    Get arbitrage statistics summary
    """
    try:
        opportunities = arbitrage_service.find_arbitrage_opportunities()

        # Calculate statistics
        total_opportunities = len(opportunities)
        profitable_count = len([op for op in opportunities if op['spread'] > 0.1])
        avg_spread = sum(op['spread'] for op in opportunities) / max(total_opportunities, 1)

        # Top exchanges by opportunities
        exchange_counts = {}
        for op in opportunities:
            buy_ex = op['buy_exchange']
            sell_ex = op['sell_exchange']
            exchange_counts[buy_ex] = exchange_counts.get(buy_ex, 0) + 1
            exchange_counts[sell_ex] = exchange_counts.get(sell_ex, 0) + 1

        top_exchanges = sorted(
            exchange_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        stats = {
            'total_opportunities': total_opportunities,
            'profitable_opportunities': profitable_count,
            'average_spread': round(avg_spread, 3),
            'top_exchanges': [{'name': name, 'count': count} for name, count in top_exchanges]
        }

        return jsonify({
            'status': 'success',
            'data': stats
        })

    except Exception as e:
        logger.error(f"Arbitrage stats API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load arbitrage statistics'
        }), 500


@arbitrage_bp.route('/exchanges')
def api_exchanges():
    """
    Get list of available exchanges and their status
    """
    try:
        exchange_services = get_all_exchange_services()
        exchanges = []

        for name, service in exchange_services.items():
            try:
                # Test if exchange is responsive
                data = service.get_cached_trading_data()
                symbol_count = len(data)
                status = 'active' if symbol_count > 0 else 'inactive'

                exchanges.append({
                    'name': name,
                    'status': status,
                    'symbol_count': symbol_count,
                    'last_updated': service._trading_cache_time if hasattr(service, '_trading_cache_time') else None
                })

            except Exception as e:
                logger.warning(f"Exchange {name} error: {e}")
                exchanges.append({
                    'name': name,
                    'status': 'error',
                    'symbol_count': 0,
                    'last_updated': None
                })

        return jsonify({
            'status': 'success',
            'data': {
                'exchanges': exchanges,
                'total': len(exchanges),
                'active': len([ex for ex in exchanges if ex['status'] == 'active'])
            }
        })

    except Exception as e:
        logger.error(f"Exchanges API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load exchange information'
        }), 500


@arbitrage_bp.route('/tokens')
def api_tokens():
    """
    Get tokens with arbitrage opportunities
    """
    try:
        exchange_filter = request.args.get('exchange', None)
        sort_by = request.args.get('sort', 'spread')  # spread, volume, symbol
        order = request.args.get('order', 'desc')  # asc, desc

        opportunities = arbitrage_service.find_arbitrage_opportunities(
            exchange_filter=exchange_filter
        )

        # Group by token
        tokens_data = {}
        for op in opportunities:
            symbol = op['symbol']
            if symbol not in tokens_data:
                tokens_data[symbol] = {
                    'symbol': symbol,
                    'token': symbol.replace('USDT', ''),
                    'opportunities': [],
                    'best_spread': 0,
                    'total_volume': 0
                }

            tokens_data[symbol]['opportunities'].append(op)
            tokens_data[symbol]['best_spread'] = max(
                tokens_data[symbol]['best_spread'],
                op['spread']
            )
            tokens_data[symbol]['total_volume'] += op.get('volume', 0)

        # Convert to list and sort
        tokens_list = list(tokens_data.values())

        if sort_by == 'spread':
            tokens_list.sort(key=lambda x: x['best_spread'], reverse=(order == 'desc'))
        elif sort_by == 'volume':
            tokens_list.sort(key=lambda x: x['total_volume'], reverse=(order == 'desc'))
        elif sort_by == 'symbol':
            tokens_list.sort(key=lambda x: x['symbol'], reverse=(order == 'desc'))

        return jsonify({
            'status': 'success',
            'data': {
                'tokens': tokens_list,
                'total': len(tokens_list),
                'filters': {
                    'exchange': exchange_filter,
                    'sort': sort_by,
                    'order': order
                }
            }
        })

    except Exception as e:
        logger.error(f"Tokens API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load token information'
        }), 500


@arbitrage_bp.route('/refresh')
def api_refresh_cache():
    """
    Force refresh of exchange data caches
    """
    try:
        exchange_services = get_all_exchange_services()

        # Clear all caches
        refreshed = []
        errors = []

        for name, service in exchange_services.items():
            try:
                service.clear_cache()
                # Force refresh by requesting new data
                service.get_cached_trading_data()
                service.get_cached_networks_data()
                refreshed.append(name)
            except Exception as e:
                logger.error(f"Failed to refresh {name}: {e}")
                errors.append({'exchange': name, 'error': str(e)})

        return jsonify({
            'status': 'success',
            'data': {
                'refreshed': refreshed,
                'errors': errors,
                'total_refreshed': len(refreshed)
            }
        })

    except Exception as e:
        logger.error(f"Cache refresh API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to refresh cache'
        }), 500


# Legacy endpoints for backward compatibility
@arbitrage_bp.route('/data')
def legacy_api_data():
    """
    Legacy API endpoint for table data
    """
    try:
        table_data = arbitrage_service.get_table_data()

        # Return in legacy format
        return jsonify({
            'status': 'success',
            'data': table_data
        })

    except Exception as e:
        logger.error(f"Legacy API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load table data'
        }), 500