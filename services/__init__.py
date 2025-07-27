"""
Services package initialization
Exports all exchange services and utilities
"""

# Import base classes and utilities
from .exchanges.base import (
    BaseExchangeService,
    ExchangeManager,
    get_exchange_manager,
    register_all_exchanges
)

# Import arbitrage service
from .arbitrage import ArbitrageService

# Export all services
__all__ = [
    'BaseExchangeService',
    'ExchangeManager',
    'get_exchange_manager',
    'register_all_exchanges',
    'ArbitrageService'
]

# Helper function to get all exchange services
def get_all_exchange_services():
    """Get all available exchange services from the manager"""
    return get_exchange_manager().get_all_exchanges()