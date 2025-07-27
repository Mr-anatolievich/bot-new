"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import os
from app import create_app
from models import db


@pytest.fixture
def app():
    """Create application for testing"""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()

    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner"""
    return app.test_cli_runner()