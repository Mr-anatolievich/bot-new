#!/usr/bin/env python3
"""
Arbitrage Bot - Main Flask Application
Modern API-first architecture with React SPA frontend
"""

import os
import logging
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Import configuration
from config.settings import get_config

# Import models
from models import db

# Initialize Flask extensions
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__,
                static_folder='static',
                static_url_path='/static')

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Configure logging
    setup_logging(app)

    # Initialize extensions
    setup_extensions(app)

    # Setup CORS for React development
    setup_cors(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Setup React SPA routes
    setup_spa_routes(app)

    # Register CLI commands
    register_cli_commands(app)

    app.logger.info("Arbitrage Bot initialized successfully")
    return app


def register_cli_commands(app):
    """Register CLI commands"""
    try:
        from cli import register_commands
        register_commands(app)
    except ImportError:
        app.logger.warning("CLI commands not available")


def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s'
        )


def setup_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # Initialize exchange services
    with app.app_context():
        from services import register_all_exchanges
        register_all_exchanges()
        app.logger.info("Exchange services initialized")

    # Create database tables
    with app.app_context():
        db.create_all()


def setup_cors(app):
    """Setup CORS for React development"""
    if app.config['DEBUG']:
        CORS(app, resources={
            r"/api/*": {
                "origins": app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
            }
        })


def register_blueprints(app):
    """Register application blueprints"""
    try:
        # Import and register route blueprints
        from routes.arbitrage import arbitrage_bp
        from routes.tokens import tokens_bp
        from routes.networks import networks_bp

        app.register_blueprint(arbitrage_bp, url_prefix='/api/v1')
        app.register_blueprint(tokens_bp, url_prefix='/api/v1')
        app.register_blueprint(networks_bp, url_prefix='/api/v1')

        app.logger.info("All blueprints registered successfully")

    except ImportError as e:
        app.logger.error(f"Failed to import blueprints: {e}")
        # Create minimal fallback routes
        create_fallback_routes(app)


def create_fallback_routes(app):
    """Create fallback API routes if blueprints fail"""
    @app.route('/api/v1/dashboard')
    @limiter.limit("30 per minute")
    def fallback_dashboard():
        """Fallback dashboard endpoint"""
        return jsonify({
            'status': 'success',
            'data': {
                'stats': [
                    {
                        'title': 'Total Profit (24h)',
                        'value': '$0.00',
                        'change': '+0.0%',
                        'icon': 'fas fa-wallet',
                        'color': 'primary'
                    }
                ],
                'recent_trades': [],
                'top_tokens': []
            }
        })

    @app.route('/api/v1/arbitrage')
    @limiter.limit("30 per minute")
    def fallback_arbitrage():
        """Fallback arbitrage endpoint"""
        return jsonify({
            'status': 'success',
            'data': {
                'opportunities': [],
                'total': 0
            }
        })


def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        if app.config['DEBUG']:
            return jsonify({'error': 'Not found', 'message': str(error)}), 404
        # For production, serve React app for unknown routes (SPA routing)
        return serve_react_app()

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Rate limit exceeded', 'message': str(e)}), 429


def setup_spa_routes(app):
    """Setup routes for React SPA"""
    @app.route('/')
    def index():
        """Serve React SPA"""
        return serve_react_app()

    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'environment': 'development' if app.config['DEBUG'] else 'production'
        })

    # Serve React static files
    @app.route('/static/js/<path:filename>')
    def serve_js(filename):
        """Serve JavaScript files"""
        return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

    @app.route('/static/css/<path:filename>')
    def serve_css(filename):
        """Serve CSS files"""
        return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

    # Catch-all route for React Router
    @app.route('/<path:path>')
    def spa_routing(path):
        """SPA routing - serve React app for client-side routing"""
        if not path.startswith(('api/', 'static/', 'health')):
            return serve_react_app()
        return jsonify({'error': 'Not found'}), 404


def serve_react_app():
    """Serve React application"""
    try:
        # Try to serve built React app
        react_build_path = os.path.join('static', 'build', 'index.html')
        if os.path.exists(react_build_path):
            return send_file(react_build_path)

        # Fallback to development template
        from flask import render_template
        return render_template('index.html')

    except Exception as e:
        logging.error(f"Failed to serve React app: {e}")
        return jsonify({
            'error': 'Application not available',
            'message': 'Please check if React build exists or run in development mode'
        }), 503


# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    if debug:
        app.logger.info("🚀 Starting Arbitrage Bot API Server")
        app.logger.info(f"📱 API: http://{host}:{port}/api/v1")
        app.logger.info(f"🔗 Frontend: http://{host}:{port}")
        app.logger.info(f"💚 Health: http://{host}:{port}/health")

    app.run(host=host, port=port, debug=debug, threaded=True)