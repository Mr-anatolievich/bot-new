"""
Trade model for storing executed trades
"""

from .base import db, BaseModel


class Trade(BaseModel):
    """Model for storing arbitrage trades"""
    __tablename__ = 'trades'

    # Trade details
    symbol = db.Column(db.String(20), nullable=False, index=True)
    buy_exchange = db.Column(db.String(50), nullable=False)
    sell_exchange = db.Column(db.String(50), nullable=False)

    # Prices and amounts
    buy_price = db.Column(db.Numeric(20, 8), nullable=False)
    sell_price = db.Column(db.Numeric(20, 8), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)

    # Calculated values
    gross_profit = db.Column(db.Numeric(20, 8))
    fees_paid = db.Column(db.Numeric(20, 8))
    net_profit = db.Column(db.Numeric(20, 8))
    spread_percentage = db.Column(db.Numeric(8, 4))

    # Status and timing
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, completed, failed
    execution_time = db.Column(db.Integer)  # milliseconds

    # Network used for transfer
    network = db.Column(db.String(50))

    def __repr__(self):
        return f'<Trade {self.symbol} {self.buy_exchange}→{self.sell_exchange}>'


class Exchange(BaseModel):
    """Model for storing exchange information"""
    __tablename__ = 'exchanges'

    name = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, inactive, error
    api_connected = db.Column(db.Boolean, default=False)
    last_data_update = db.Column(db.DateTime)
    error_message = db.Column(db.Text)

    def __repr__(self):
        return f'<Exchange {self.name}>'


class ArbitrageOpportunity(BaseModel):
    """Model for storing arbitrage opportunities"""
    __tablename__ = 'arbitrage_opportunities'

    symbol = db.Column(db.String(20), nullable=False, index=True)
    buy_exchange = db.Column(db.String(50), nullable=False)
    sell_exchange = db.Column(db.String(50), nullable=False)

    buy_price = db.Column(db.Numeric(20, 8), nullable=False)
    sell_price = db.Column(db.Numeric(20, 8), nullable=False)
    spread_percentage = db.Column(db.Numeric(8, 4), nullable=False)

    volume_24h = db.Column(db.Numeric(20, 8))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Opportunity {self.symbol} {self.spread_percentage}%>'