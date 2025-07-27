"""
Tokens API routes
"""

from flask import Blueprint, jsonify, request
import logging

from services import get_all_exchange_services

# Create blueprint
tokens_bp = Blueprint('tokens', __name__)
logger = logging.getLogger(__name__)


@tokens_bp.route('/tokens')
def api_all_tokens():
    """
    Get tokens data from all exchanges
    Returns formatted data for each exchange
    """
    try:
        exchange_services = get_all_exchange_services()
        exchanges_data = {}

        for exchange_name, service in exchange_services.items():
            try:
                # Get trading and networks data
                trading_data = service.get_cached_trading_data()
                formatted_tokens = service.format_token_data(trading_data)

                exchanges_data[exchange_name.lower()] = {
                    'name': exchange_name,
                    'status': 'active' if formatted_tokens else 'inactive',
                    'tokens': formatted_tokens,
                    'count': len(formatted_tokens)
                }

            except Exception as e:
                logger.error(f"Error processing {exchange_name}: {e}")
                exchanges_data[exchange_name.lower()] = {
                    'name': exchange_name,
                    'status': 'error',
                    'tokens': [],
                    'count': 0,
                    'error': str(e)
                }

        return jsonify({
            'status': 'success',
            'data': {
                'exchanges': exchanges_data,
                'total_exchanges': len(exchanges_data)
            }
        })

    except Exception as e:
        logger.error(f"Tokens API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load tokens data'
        }), 500


@tokens_bp.route('/tokens/<exchange_id>')
def api_tokens_by_exchange(exchange_id):
    """
    Get tokens data for specific exchange
    """
    try:
        exchange_services = get_all_exchange_services()

        # Find exchange by ID (case insensitive)
        exchange_service = None
        exchange_name = None

        for name, service in exchange_services.items():
            if name.lower() == exchange_id.lower():
                exchange_service = service
                exchange_name = name
                break

        if not exchange_service:
            return jsonify({
                'status': 'error',
                'message': f'Exchange "{exchange_id}" not found'
            }), 404

        # Get trading data
        trading_data = exchange_service.get_cached_trading_data()

        if not trading_data:
            return jsonify({
                'status': 'error',
                'message': f'No data available for {exchange_name}'
            }), 503

        # Format tokens data
        formatted_tokens = exchange_service.format_token_data(trading_data)

        return jsonify({
            'status': 'success',
            'data': {
                'exchange': exchange_name,
                'tokens': formatted_tokens,
                'count': len(formatted_tokens),
                'last_updated': getattr(exchange_service, '_trading_cache_time', None)
            }
        })

    except Exception as e:
        logger.error(f"Error processing {exchange_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@tokens_bp.route('/tokens/search')
def api_search_tokens():
    """
    Search tokens across all exchanges
    """
    try:
        query = request.args.get('q', '').strip().upper()
        exchange_filter = request.args.get('exchange', None)
        min_volume = request.args.get('min_volume', 0, type=float)
        sort_by = request.args.get('sort', 'volume')  # volume, symbol, spread
        limit = request.args.get('limit', 100, type=int)

        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Search query parameter "q" is required'
            }), 400

        exchange_services = get_all_exchange_services()
        found_tokens = []

        for exchange_name, service in exchange_services.items():
            # Apply exchange filter
            if exchange_filter and exchange_filter.lower() != exchange_name.lower():
                continue

            try:
                trading_data = service.get_cached_trading_data()

                for symbol, data in trading_data.items():
                    # Search in symbol name
                    if query in symbol:
                        volume = data.get('volume', 0)

                        # Apply volume filter
                        if volume < min_volume:
                            continue

                        # Calculate spread
                        spread = 0
                        if data.get('ask', 0) > 0:
                            spread = ((data.get('bid', 0) - data['ask']) / data['ask']) * 100

                        found_tokens.append({
                            'symbol': symbol,
                            'exchange': exchange_name,
                            'bid': data.get('bid', 0),
                            'ask': data.get('ask', 0),
                            'last': data.get('last', 0),
                            'volume': volume,
                            'spread': spread,
                            'price_change': data.get('priceChangePercent', 0)
                        })

            except Exception as e:
                logger.warning(f"Error searching in {exchange_name}: {e}")
                continue

        # Sort results
        if sort_by == 'volume':
            found_tokens.sort(key=lambda x: x['volume'], reverse=True)
        elif sort_by == 'symbol':
            found_tokens.sort(key=lambda x: x['symbol'])
        elif sort_by == 'spread':
            found_tokens.sort(key=lambda x: x['spread'], reverse=True)

        # Apply limit
        limited_tokens = found_tokens[:limit]

        return jsonify({
            'status': 'success',
            'data': {
                'tokens': limited_tokens,
                'total_found': len(found_tokens),
                'returned': len(limited_tokens),
                'query': query,
                'filters': {
                    'exchange': exchange_filter,
                    'min_volume': min_volume,
                    'sort': sort_by,
                    'limit': limit
                }
            }
        })

    except Exception as e:
        logger.error(f"Token search API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to search tokens'
        }), 500


@tokens_bp.route('/tokens/top')
def api_top_tokens():
    """
    Get top tokens by various metrics
    """
    try:
        metric = request.args.get('metric', 'volume')  # volume, price_change, spread
        limit = request.args.get('limit', 20, type=int)
        exchange_filter = request.args.get('exchange', None)

        exchange_services = get_all_exchange_services()
        all_tokens = []

        for exchange_name, service in exchange_services.items():
            # Apply exchange filter
            if exchange_filter and exchange_filter.lower() != exchange_name.lower():
                continue

            try:
                trading_data = service.get_cached_trading_data()

                for symbol, data in trading_data.items():
                    volume = data.get('volume', 0)
                    price_change = data.get('priceChangePercent', 0)

                    # Calculate spread
                    spread = 0
                    if data.get('ask', 0) > 0:
                        spread = ((data.get('bid', 0) - data['ask']) / data['ask']) * 100

                    all_tokens.append({
                        'symbol': symbol,
                        'exchange': exchange_name,
                        'volume': volume,
                        'price_change': price_change,
                        'spread': spread,
                        'bid': data.get('bid', 0),
                        'ask': data.get('ask', 0),
                        'last': data.get('last', 0)
                    })

            except Exception as e:
                logger.warning(f"Error processing {exchange_name}: {e}")
                continue

        # Sort by metric
        if metric == 'volume':
            all_tokens.sort(key=lambda x: x['volume'], reverse=True)
        elif metric == 'price_change':
            all_tokens.sort(key=lambda x: abs(x['price_change']), reverse=True)
        elif metric == 'spread':
            all_tokens.sort(key=lambda x: abs(x['spread']), reverse=True)

        # Apply limit
        top_tokens = all_tokens[:limit]

        return jsonify({
            'status': 'success',
            'data': {
                'tokens': top_tokens,
                'metric': metric,
                'total_analyzed': len(all_tokens),
                'returned': len(top_tokens),
                'filters': {
                    'exchange': exchange_filter,
                    'limit': limit
                }
            }
        })

    except Exception as e:
        logger.error(f"Top tokens API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get top tokens'
        }), 500


@tokens_bp.route('/tokens/compare/<symbol>')
def api_compare_token(symbol):
    """
    Compare token prices across all exchanges
    """
    try:
        symbol = symbol.upper()
        exchange_services = get_all_exchange_services()
        comparisons = []

        for exchange_name, service in exchange_services.items():
            try:
                trading_data = service.get_cached_trading_data()

                # Look for exact match or normalized symbol
                token_data = None
                for s, data in trading_data.items():
                    if s == symbol or service.normalize_symbol(s) == service.normalize_symbol(symbol):
                        token_data = data
                        break

                if token_data:
                    bid = token_data.get('bid', 0)
                    ask = token_data.get('ask', 0)
                    spread = ((bid - ask) / ask * 100) if ask > 0 else 0

                    comparisons.append({
                        'exchange': exchange_name,
                        'symbol': token_data.get('symbol', symbol),
                        'bid': bid,
                        'ask': ask,
                        'last': token_data.get('last', 0),
                        'volume': token_data.get('volume', 0),
                        'spread': spread,
                        'available': True
                    })
                else:
                    comparisons.append({
                        'exchange': exchange_name,
                        'symbol': symbol,
                        'available': False
                    })

            except Exception as e:
                logger.warning(f"Error comparing token on {exchange_name}: {e}")
                comparisons.append({
                    'exchange': exchange_name,
                    'symbol': symbol,
                    'available': False,
                    'error': str(e)
                })

        # Calculate statistics
        available_prices = [c for c in comparisons if c.get('available')]

        stats = {}
        if available_prices:
            asks = [c['ask'] for c in available_prices if c['ask'] > 0]
            bids = [c['bid'] for c in available_prices if c['bid'] > 0]

            if asks and bids:
                stats = {
                    'highest_bid': max(bids),
                    'lowest_ask': min(asks),
                    'price_spread': ((max(bids) - min(asks)) / min(asks) * 100) if min(asks) > 0 else 0,
                    'available_exchanges': len(available_prices),
                    'total_exchanges': len(comparisons)
                }

        return jsonify({
            'status': 'success',
            'data': {
                'symbol': symbol,
                'comparisons': comparisons,
                'statistics': stats
            }
        })

    except Exception as e:
        logger.error(f"Token comparison API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to compare token'
        }), 500