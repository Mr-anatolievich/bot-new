"""
Exchange services package initialization
"""

from .base import BaseExchangeService, ExchangeManager, get_exchange_manager

__all__ = ['BaseExchangeService', 'ExchangeManager', 'get_exchange_manager']

# Individual exchange services
try:
    from .binance import BinanceService
    __all__.append('BinanceService')
except ImportError:
    pass

try:
    from .bybit import BybitService
    __all__.append('BybitService')
except ImportError:
    pass

try:
    from .kucoin import KucoinService
    __all__.append('KucoinService')
except ImportError:
    pass

# Import stub services
try:
    from .stub_services import GateioService, HuobiService, MexcService, BitgetService
    __all__.extend(['GateioService', 'HuobiService', 'MexcService', 'BitgetService'])
except ImportError:
    pass