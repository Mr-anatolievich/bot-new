"""
Application configuration settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///arbitrage.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # API Rate limiting
    RATELIMIT_STORAGE_URI = os.getenv('REDIS_URL', 'memory://')

    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Exchange API Keys
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY')
    BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET')

    OKXAPI_KEY = os.getenv('OKX_API_KEY')
    OKX_API_SECRET = os.getenv('OKX_API_SECRET')
    OKX_PASSPHRASE = os.getenv('OKX_PASSPHRASE')

    KUCOIN_API_KEY = os.getenv('KUCOIN_API_KEY')
    KUCOIN_API_SECRET = os.getenv('KUCOIN_API_SECRET')
    KUCOIN_API_PASSPHRASE = os.getenv('KUCOIN_API_PASSPHRASE')

    GATEIO_API_KEY = os.getenv('GATEIO_API_KEY')
    GATEIO_API_SECRET = os.getenv('GATEIO_API_SECRET')

    HUOBI_API_KEY = os.getenv('HUOBI_API_KEY')
    HUOBI_API_SECRET = os.getenv('HUOBI_API_SECRET')

    MEXC_API_KEY = os.getenv('MEXC_API_KEY')
    MEXC_API_SECRET = os.getenv('MEXC_API_SECRET')

    BITGET_API_KEY = os.getenv('BITGET_API_KEY')
    BITGET_API_SECRET = os.getenv('BITGET_API_SECRET')
    BITGET_API_PASSPHRASE = os.getenv('BITGET_API_PASSPHRASE')

    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # Application settings
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', 3600))  # 1 hour
    MIN_ARBITRAGE_SPREAD = float(os.getenv('MIN_ARBITRAGE_SPREAD', 0.1))  # 0.1%


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

    # CORS settings for React development
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Production database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/arbitrage')

    # Production CORS settings
    CORS_ORIGINS = [os.getenv('FRONTEND_URL', 'https://yourdomain.com')]


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

    # In-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    return config_map.get(config_name, config_map['default'])