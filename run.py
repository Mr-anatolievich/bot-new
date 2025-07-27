#!/usr/bin/env python3
"""
Development server runner
Simple script to run the Flask application in development mode
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import create_app

    # Create Flask app
    app = create_app('development')

    # Configuration
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print("🚀 Starting Arbitrage Bot Development Server")
    print(f"📱 Frontend: http://{host}:{port}")
    print(f"🔗 API: http://{host}:{port}/api/v1")
    print(f"💚 Health: http://{host}:{port}/health")
    print("Press CTRL+C to stop the server")
    print("-" * 50)

    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

except ImportError as e:
    print(f"❌ Error importing application: {e}")
    print("💡 Make sure you have installed all dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)