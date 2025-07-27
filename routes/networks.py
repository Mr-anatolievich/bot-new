"""
Networks API routes
Handles withdrawal networks, fees, and deposit information
"""

from flask import Blueprint, jsonify, request
import logging
from collections import defaultdict

from services import get_all_exchange_services
from services.exchanges.base import BaseExchangeService

# Create blueprint
networks_bp = Blueprint('networks', __name__)
logger = logging.getLogger(__name__)


@networks_bp.route('/networks')
def api_all_networks():
    """
    Get all networks data from all exchanges
    Returns comprehensive network information
    """
    try:
        exchange_services = get_all_exchange_services()
        networks_data = []

        for exchange_name, service in exchange_services.items():
            try:
                exchange_networks = service.get_cached_networks_data()

                for token, networks in exchange_networks.items():
                    for network in networks:
                        networks_data.append({
                            'token': token,
                            'exchange': exchange_name,
                            'network': network.get('name', ''),
                            'deposit': network.get('deposit', False),
                            'withdraw': network.get('withdraw', False),
                            'fee': network.get('fee', '0'),
                            'min_withdraw': network.get('min_withdraw', '0'),
                            'max_withdraw': network.get('max_withdraw', '0'),
                            'confirm_times': network.get('confirm_times', 0)
                        })

            except Exception as e:
                logger.error(f"Error processing networks for {exchange_name}: {e}")
                continue

        return jsonify({
            'status': 'success',
            'data': {
                'networks': networks_data,
                'total': len(networks_data),
                'unique_tokens': len(set(n['token'] for n in networks_data)),
                'unique_networks': len(set(n['network'] for n in networks_data))
            }
        })

    except Exception as e:
        logger.error(f"Networks API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load networks data'
        }), 500


@networks_bp.route('/networks/<token>')
def api_token_networks(token):
    """
    Get network information for specific token
    """
    try:
        token = token.upper()
        exchange_services = get_all_exchange_services()
        token_networks = []

        for exchange_name, service in exchange_services.items():
            try:
                exchange_networks = service.get_cached_networks_data()

                if token in exchange_networks:
                    for network in exchange_networks[token]:
                        token_networks.append({
                            'exchange': exchange_name,
                            'network': network.get('name', ''),
                            'deposit': network.get('deposit', False),
                            'withdraw': network.get('withdraw', False),
                            'fee': network.get('fee', '0'),
                            'min_withdraw': network.get('min_withdraw', '0'),
                            'max_withdraw': network.get('max_withdraw', '0'),
                            'confirm_times': network.get('confirm_times', 0)
                        })

            except Exception as e:
                logger.warning(f"Error getting networks for {token} from {exchange_name}: {e}")
                continue

        if not token_networks:
            return jsonify({
                'status': 'error',
                'message': f'Token "{token}" not found on any exchange'
            }), 404

        # Group by network name
        grouped_networks = defaultdict(list)
        for network in token_networks:
            grouped_networks[network['network']].append(network)

        return jsonify({
            'status': 'success',
            'data': {
                'token': token,
                'networks': dict(grouped_networks),
                'total_entries': len(token_networks),
                'available_exchanges': len(set(n['exchange'] for n in token_networks)),
                'supported_networks': list(grouped_networks.keys())
            }
        })

    except Exception as e:
        logger.error(f"Token networks API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load token networks'
        }), 500


@networks_bp.route('/networks/compare/<token>')
def api_compare_network_fees(token):
    """
    Compare withdrawal fees for a token across all exchanges and networks
    """
    try:
        token = token.upper()
        exchange_services = get_all_exchange_services()
        fee_comparison = []

        for exchange_name, service in exchange_services.items():
            try:
                exchange_networks = service.get_cached_networks_data()

                if token in exchange_networks:
                    for network in exchange_networks[token]:
                        if network.get('withdraw', False):
                            try:
                                fee = float(network.get('fee', 0))
                                fee_comparison.append({
                                    'exchange': exchange_name,
                                    'network': network.get('name', ''),
                                    'fee': fee,
                                    'fee_str': network.get('fee', '0'),
                                    'min_withdraw': network.get('min_withdraw', '0'),
                                    'confirm_times': network.get('confirm_times', 0)
                                })
                            except ValueError:
                                # Handle non-numeric fees
                                fee_comparison.append({
                                    'exchange': exchange_name,
                                    'network': network.get('name', ''),
                                    'fee': 0,
                                    'fee_str': network.get('fee', '0'),
                                    'min_withdraw': network.get('min_withdraw', '0'),
                                    'confirm_times': network.get('confirm_times', 0)
                                })

            except Exception as e:
                logger.warning(f"Error comparing fees for {token} from {exchange_name}: {e}")
                continue

        if not fee_comparison:
            return jsonify({
                'status': 'error',
                'message': f'No withdrawal data found for token "{token}"'
            }), 404

        # Sort by fee (lowest first)
        fee_comparison.sort(key=lambda x: x['fee'])

        # Calculate statistics
        fees = [f['fee'] for f in fee_comparison if f['fee'] > 0]
        stats = {}

        if fees:
            stats = {
                'lowest_fee': min(fees),
                'highest_fee': max(fees),
                'average_fee': sum(fees) / len(fees),
                'cheapest_option': fee_comparison[0] if fee_comparison else None
            }

        return jsonify({
            'status': 'success',
            'data': {
                'token': token,
                'fee_comparison': fee_comparison,
                'statistics': stats,
                'total_options': len(fee_comparison)
            }
        })

    except Exception as e:
        logger.error(f"Network fees comparison API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to compare network fees'
        }), 500


@networks_bp.route('/networks/cheapest')
def api_cheapest_networks():
    """
    Get cheapest withdrawal options for all tokens
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        network_filter = request.args.get('network', None)

        exchange_services = get_all_exchange_services()
        cheapest_options = []

        # Collect all tokens
        all_tokens = set()
        for service in exchange_services.values():
            try:
                networks_data = service.get_cached_networks_data()
                all_tokens.update(networks_data.keys())
            except Exception as e:
                logger.warning(f"Error collecting tokens: {e}")
                continue

        # Find cheapest option for each token
        for token in all_tokens:
            token_options = []

            for exchange_name, service in exchange_services.items():
                try:
                    exchange_networks = service.get_cached_networks_data()

                    if token in exchange_networks:
                        for network in exchange_networks[token]:
                            if network.get('withdraw', False):
                                # Apply network filter
                                if network_filter and network_filter.lower() not in network.get('name', '').lower():
                                    continue

                                try:
                                    fee = float(network.get('fee', 0))
                                    token_options.append({
                                        'token': token,
                                        'exchange': exchange_name,
                                        'network': network.get('name', ''),
                                        'fee': fee,
                                        'fee_str': network.get('fee', '0'),
                                        'min_withdraw': network.get('min_withdraw', '0')
                                    })
                                except ValueError:
                                    continue

                except Exception as e:
                    logger.warning(f"Error processing {token} from {exchange_name}: {e}")
                    continue

            # Find cheapest option for this token
            if token_options:
                cheapest = min(token_options, key=lambda x: x['fee'])
                cheapest_options.append(cheapest)

        # Sort by fee and apply limit
        cheapest_options.sort(key=lambda x: x['fee'])
        limited_options = cheapest_options[:limit]

        return jsonify({
            'status': 'success',
            'data': {
                'cheapest_options': limited_options,
                'total_analyzed': len(cheapest_options),
                'returned': len(limited_options),
                'filters': {
                    'network': network_filter,
                    'limit': limit
                }
            }
        })

    except Exception as e:
        logger.error(f"Cheapest networks API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get cheapest networks'
        }), 500


@networks_bp.route('/networks/supported')
def api_supported_networks():
    """
    Get list of all supported networks across exchanges
    """
    try:
        exchange_services = get_all_exchange_services()
        network_stats = defaultdict(lambda: {
            'exchanges': [],
            'tokens': set(),
            'total_pairs': 0
        })

        for exchange_name, service in exchange_services.items():
            try:
                exchange_networks = service.get_cached_networks_data()

                for token, networks in exchange_networks.items():
                    for network in networks:
                        network_name = network.get('name', '')
                        if network_name:
                            network_stats[network_name]['exchanges'].append(exchange_name)
                            network_stats[network_name]['tokens'].add(token)
                            network_stats[network_name]['total_pairs'] += 1

            except Exception as e:
                logger.warning(f"Error processing networks from {exchange_name}: {e}")
                continue

        # Format results
        formatted_networks = []
        for network_name, stats in network_stats.items():
            formatted_networks.append({
                'network': network_name,
                'supported_exchanges': list(set(stats['exchanges'])),
                'exchange_count': len(set(stats['exchanges'])),
                'supported_tokens': list(stats['tokens']),
                'token_count': len(stats['tokens']),
                'total_pairs': stats['total_pairs']
            })

        # Sort by popularity (exchange count)
        formatted_networks.sort(key=lambda x: x['exchange_count'], reverse=True)

        return jsonify({
            'status': 'success',
            'data': {
                'networks': formatted_networks,
                'total_networks': len(formatted_networks),
                'most_popular': formatted_networks[0] if formatted_networks else None
            }
        })

    except Exception as e:
        logger.error(f"Supported networks API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get supported networks'
        }), 500


@networks_bp.route('/networks/status')
def api_networks_status():
    """
    Get network status summary across all exchanges
    """
    try:
        exchange_services = get_all_exchange_services()
        status_summary = {
            'exchanges': {},
            'totals': {
                'total_tokens': 0,
                'total_networks': 0,
                'deposit_enabled': 0,
                'withdraw_enabled': 0
            }
        }

        all_tokens = set()
        all_networks = set()

        for exchange_name, service in exchange_services.items():
            try:
                exchange_networks = service.get_cached_networks_data()

                exchange_stats = {
                    'tokens': len(exchange_networks),
                    'total_networks': 0,
                    'deposit_enabled': 0,
                    'withdraw_enabled': 0,
                    'last_updated': getattr(service, '_networks_cache_time', None)
                }

                for token, networks in exchange_networks.items():
                    all_tokens.add(token)

                    for network in networks:
                        network_name = network.get('name', '')
                        if network_name:
                            all_networks.add(network_name)
                            exchange_stats['total_networks'] += 1

                            if network.get('deposit', False):
                                exchange_stats['deposit_enabled'] += 1

                            if network.get('withdraw', False):
                                exchange_stats['withdraw_enabled'] += 1

                status_summary['exchanges'][exchange_name] = exchange_stats

            except Exception as e:
                logger.warning(f"Error getting status for {exchange_name}: {e}")
                status_summary['exchanges'][exchange_name] = {
                    'tokens': 0,
                    'total_networks': 0,
                    'deposit_enabled': 0,
                    'withdraw_enabled': 0,
                    'error': str(e)
                }

        # Calculate totals
        status_summary['totals'] = {
            'unique_tokens': len(all_tokens),
            'unique_networks': len(all_networks),
            'total_exchanges': len(exchange_services),
            'active_exchanges': len([ex for ex in status_summary['exchanges'].values() if ex.get('tokens', 0) > 0])
        }

        return jsonify({
            'status': 'success',
            'data': status_summary
        })

    except Exception as e:
        logger.error(f"Networks status API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get networks status'
        }), 500