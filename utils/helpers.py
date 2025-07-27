"""
Helper utilities for the application
"""
import re
import time
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from functools import wraps
from flask import jsonify, request


logger = logging.getLogger(__name__)


def standardize_response(data: Any = None, message: str = None, status: str = 'success',
                         status_code: int = 200) -> tuple:
    """
    Standardize API response format

    Args:
        data: Response data
        message: Optional message
        status: Response status ('success', 'error', 'warning')
        status_code: HTTP status code

    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        'status': status,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

    if data is not None:
        response['data'] = data

    if message:
        response['message'] = message

    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400, details: Dict = None) -> tuple:
    """Create standardized error response"""
    error_data = {'message': message}
    if details:
        error_data['details'] = details

    return standardize_response(
        data=error_data,
        status='error',
        status_code=status_code
    )


def success_response(data: Any = None, message: str = None) -> tuple:
    """Create standardized success response"""
    return standardize_response(data=data, message=message, status='success')


def validate_pagination_params(request_args) -> Dict[str, int]:
    """
    Validate and extract pagination parameters

    Args:
        request_args: Flask request.args

    Returns:
        Dict with 'page', 'per_page', 'offset' keys
    """
    try:
        page = max(1, int(request_args.get('page', 1)))
        per_page = min(1000, max(1, int(request_args.get('per_page', 50))))
        offset = (page - 1) * per_page

        return {
            'page': page,
            'per_page': per_page,
            'offset': offset
        }
    except ValueError:
        return {
            'page': 1,
            'per_page': 50,
            'offset': 0
        }


def validate_sort_params(request_args, valid_fields: List[str]) -> Dict[str, str]:
    """
    Validate sorting parameters

    Args:
        request_args: Flask request.args
        valid_fields: List of valid field names for sorting

    Returns:
        Dict with 'sort_by' and 'order' keys
    """
    sort_by = request_args.get('sort', valid_fields[0] if valid_fields else 'id')
    order = request_args.get('order', 'desc').lower()

    if sort_by not in valid_fields:
        sort_by = valid_fields[0] if valid_fields else 'id'

    if order not in ['asc', 'desc']:
        order = 'desc'

    return {
        'sort_by': sort_by,
        'order': order
    }


def normalize_symbol(symbol: str) -> str:
    """
    Normalize trading pair symbol
    Removes special characters and standardizes format
    """
    if not isinstance(symbol, str):
        return ''

    symbol = symbol.replace('-', '').replace('_', '').replace('/', '').upper()
    if symbol.endswith(('USDT', 'USDC')):
        return symbol[:-4] + symbol[-4:]
    return symbol


def get_base_token(symbol: str) -> str:
    """
    Extract base token from trading pair symbol
    E.g., 'BTCUSDT' -> 'BTC'
    """
    if not isinstance(symbol, str):
        return ''

    match = re.match(r'^([A-Z]+)(USDT|BTC|ETH|BUSD|USDC)$', symbol.upper())
    return match.group(1) if match else symbol


def is_stablecoin_pair(symbol: str) -> bool:
    """Check if trading pair is a stablecoin pair"""
    if not isinstance(symbol, str):
        return False
    return symbol.upper().endswith('USDT')


def calculate_spread_percentage(buy_price: float, sell_price: float) -> float:
    """
    Calculate spread percentage between buy and sell prices

    Args:
        buy_price: Price to buy at
        sell_price: Price to sell at

    Returns:
        Spread percentage
    """
    if buy_price <= 0:
        return 0.0

    return ((sell_price - buy_price) / buy_price) * 100


def format_currency(value: Union[int, float], decimal_places: int = 2) -> str:
    """Format currency value with proper decimal places"""
    try:
        return f"${float(value):,.{decimal_places}f}"
    except (ValueError, TypeError):
        return "$0.00"


def format_percentage(value: Union[int, float], decimal_places: int = 2) -> str:
    """Format percentage value"""
    try:
        return f"{float(value):.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0.00%"


def format_volume(value: Union[int, float]) -> str:
    """Format volume with K/M/B suffixes"""
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        return f"{value:.2f}"
    except (ValueError, TypeError):
        return "0"


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_cache_age(cache_time: float) -> int:
    """Get cache age in seconds"""
    return int(time.time() - cache_time)


def is_cache_expired(cache_time: float, duration: int) -> bool:
    """Check if cache is expired"""
    return time.time() - cache_time > duration


def rate_limit_key(identifier: str = None) -> str:
    """Generate rate limit key"""
    if identifier:
        return f"rate_limit_{identifier}"

    # Use IP address as default
    return f"rate_limit_{request.remote_addr}"


def log_request_info():
    """Log request information for debugging"""
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")

    if request.args:
        logger.debug(f"Query params: {dict(request.args)}")

    if request.is_json and request.json:
        logger.debug(f"JSON body: {request.json}")


def require_api_key(f):
    """Decorator to require API key for endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return error_response("API key required", 401)

        # Here you would validate the API key against your database
        # For now, just check if it's not empty
        if not api_key.strip():
            return error_response("Invalid API key", 401)

        return f(*args, **kwargs)

    return decorated_function


def timing_decorator(f):
    """Decorator to measure execution time"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time
        logger.info(f"{f.__name__} executed in {execution_time:.3f} seconds")

        return result

    return decorated_function


def handle_api_errors(f):
    """Decorator to handle common API errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"ValueError in {f.__name__}: {e}")
            return error_response(f"Invalid input: {str(e)}", 400)
        except KeyError as e:
            logger.error(f"KeyError in {f.__name__}: {e}")
            return error_response(f"Missing required field: {str(e)}", 400)
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return error_response("Internal server error", 500)

    return decorated_function


def validate_exchange_name(exchange_name: str, available_exchanges: List[str]) -> bool:
    """Validate if exchange name is supported"""
    if not exchange_name:
        return False

    return exchange_name.lower() in [ex.lower() for ex in available_exchanges]


def filter_by_volume(data: List[Dict], min_volume: float = 0) -> List[Dict]:
    """Filter data by minimum volume"""
    if min_volume <= 0:
        return data

    return [
        item for item in data
        if safe_float(item.get('volume', 0)) >= min_volume
    ]


def sort_data(data: List[Dict], sort_by: str, order: str = 'desc') -> List[Dict]:
    """Sort data by field"""
    reverse = order.lower() == 'desc'

    try:
        return sorted(
            data,
            key=lambda x: safe_float(x.get(sort_by, 0)),
            reverse=reverse
        )
    except Exception as e:
        logger.warning(f"Error sorting data: {e}")
        return data


def paginate_data(data: List[Any], page: int = 1, per_page: int = 50) -> Dict:
    """Paginate data and return pagination info"""
    total = len(data)
    offset = (page - 1) * per_page
    end = offset + per_page

    paginated_data = data[offset:end]

    return {
        'data': paginated_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_next': end < total,
            'has_prev': page > 1
        }
    }


def get_client_ip() -> str:
    """Get client IP address, considering proxies"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ.get('REMOTE_ADDR', 'unknown')