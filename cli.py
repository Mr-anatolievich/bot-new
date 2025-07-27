"""
CLI commands for the application
"""

import click
from flask.cli import with_appcontext
from models import db, Trade, Exchange, ArbitrageOpportunity
from services import get_all_exchange_services


@click.command()
@with_appcontext
def init_db():
    """Initialize the database."""
    click.echo('Initializing database...')
    db.create_all()
    click.echo('Database initialized.')


@click.command()
@with_appcontext
def drop_db():
    """Drop the database."""
    if click.confirm('Are you sure you want to drop the database?'):
        db.drop_all()
        click.echo('Database dropped.')


@click.command()
@with_appcontext
def seed_db():
    """Seed the database with sample data."""
    click.echo('Seeding database...')

    # Create sample exchanges
    exchanges = ['Binance', 'Bybit', 'KuCoin', 'Gate.io', 'Huobi', 'MEXC', 'Bitget']
    for name in exchanges:
        if not Exchange.query.filter_by(name=name).first():
            exchange = Exchange(name=name, status='active')
            db.session.add(exchange)

    db.session.commit()
    click.echo('Database seeded.')


@click.command()
@with_appcontext
def test_exchanges():
    """Test all exchange connections."""
    click.echo('Testing exchange connections...')

    exchange_services = get_all_exchange_services()

    for name, service in exchange_services.items():
        try:
            # Test basic data fetching
            trading_data = service.get_cached_trading_data()
            networks_data = service.get_cached_networks_data()

            trading_count = len(trading_data)
            networks_count = len(networks_data)

            status = "✅" if trading_count > 0 else "⚠️"
            click.echo(f'{status} {name}: {trading_count} pairs, {networks_count} tokens')

        except Exception as e:
            click.echo(f'❌ {name}: Error - {str(e)}')


@click.command()
@with_appcontext
def clear_cache():
    """Clear all exchange caches."""
    click.echo('Clearing exchange caches...')

    exchange_services = get_all_exchange_services()

    for name, service in exchange_services.items():
        service.clear_cache()
        click.echo(f'Cleared cache for {name}')

    click.echo('All caches cleared.')


@click.command()
@click.option('--min-spread', default=0.1, help='Minimum spread percentage')
@with_appcontext
def find_arbitrage(min_spread):
    """Find current arbitrage opportunities."""
    click.echo(f'Finding arbitrage opportunities (min spread: {min_spread}%)...')

    from services import ArbitrageService
    arbitrage_service = ArbitrageService()

    opportunities = arbitrage_service.find_arbitrage_opportunities(min_spread=min_spread)

    if not opportunities:
        click.echo('No arbitrage opportunities found.')
        return

    click.echo(f'Found {len(opportunities)} opportunities:\n')

    for i, opp in enumerate(opportunities[:10], 1):
        click.echo(f'{i}. {opp["symbol"]}')
        click.echo(f'   Buy: {opp["buy_exchange"]} @ ${opp["buy_price"]:.6f}')
        click.echo(f'   Sell: {opp["sell_exchange"]} @ ${opp["sell_price"]:.6f}')
        click.echo(f'   Spread: {opp["spread"]:.2f}%')
        click.echo(f'   Profit: ${opp["profit"]:.6f}\n')


@click.command()
@with_appcontext
def stats():
    """Show application statistics."""
    click.echo('Application Statistics:\n')

    # Database stats
    total_trades = Trade.query.count()
    successful_trades = Trade.query.filter_by(status='completed').count()
    total_exchanges = Exchange.query.count()
    active_exchanges = Exchange.query.filter_by(status='active').count()

    click.echo(f'📊 Database:')
    click.echo(f'   Total trades: {total_trades}')
    click.echo(f'   Successful trades: {successful_trades}')
    click.echo(f'   Total exchanges: {total_exchanges}')
    click.echo(f'   Active exchanges: {active_exchanges}\n')

    # Exchange data stats
    exchange_services = get_all_exchange_services()
    click.echo(f'🔄 Exchange Services:')

    total_pairs = 0
    total_tokens = 0

    for name, service in exchange_services.items():
        try:
            trading_data = service.get_cached_trading_data()
            networks_data = service.get_cached_networks_data()

            pairs_count = len(trading_data)
            tokens_count = len(networks_data)

            total_pairs += pairs_count
            total_tokens += tokens_count

            cache_age = getattr(service, '_trading_cache_time', 0)
            cache_status = "Fresh" if cache_age > 0 else "Empty"

            click.echo(f'   {name}: {pairs_count} pairs, {tokens_count} tokens ({cache_status})')

        except Exception as e:
            click.echo(f'   {name}: Error - {str(e)}')

    click.echo(f'\n📈 Totals:')
    click.echo(f'   Total trading pairs: {total_pairs}')
    click.echo(f'   Total tokens with networks: {total_tokens}')


@click.command()
@click.option('--backup-path', default='backup.sql', help='Backup file path')
@with_appcontext
def backup_db(backup_path):
    """Backup database to SQL file."""
    click.echo(f'Backing up database to {backup_path}...')

    # This is a simple implementation
    # In production, use proper database backup tools

    import sqlite3
    import os

    if 'sqlite' in str(db.engine.url):
        db_path = str(db.engine.url).replace('sqlite:///', '')

        if os.path.exists(db_path):
            # Simple file copy for SQLite
            import shutil
            shutil.copy2(db_path, backup_path)
            click.echo('SQLite database backed up successfully.')
        else:
            click.echo('Database file not found.')
    else:
        click.echo('Backup not implemented for this database type.')
        click.echo('Use database-specific tools for PostgreSQL/MySQL.')


def register_commands(app):
    """Register CLI commands with Flask app."""
    app.cli.add_command(init_db)
    app.cli.add_command(drop_db)
    app.cli.add_command(seed_db)
    app.cli.add_command(test_exchanges)
    app.cli.add_command(clear_cache)
    app.cli.add_command(find_arbitrage)
    app.cli.add_command(stats)
    app.cli.add_command(backup_db)