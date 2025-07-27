"""
Ініціалізація пакету сервісів.
Експортує всі необхідні утиліти та сервіси.
"""

# Імпортуємо базові класи та утиліти з правильного місця
from .exchanges.base import (
    BaseExchangeService,
    ExchangeManager,
    get_exchange_manager,
    register_all_exchanges
)

# Імпортуємо сервіс арбітражу
from .arbitrage import ArbitrageService

# Визначаємо, що буде доступно при імпорті з 'services'
__all__ = [
    'BaseExchangeService',
    'ExchangeManager',
    'get_exchange_manager',
    'register_all_exchanges',
    'ArbitrageService'
]

# Допоміжна функція (за бажанням)
def get_all_exchange_services():
    """Повертає всі доступні сервіси бірж з менеджера."""
    return get_exchange_manager().get_all_exchanges()