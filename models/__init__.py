"""
Database models
"""

from .base import db
from .trade import Trade, Exchange, ArbitrageOpportunity

__all__ = ['db', 'Trade', 'Exchange', 'ArbitrageOpportunity']