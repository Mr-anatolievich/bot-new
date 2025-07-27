import sys
import os
import pytest
from flask import Flask

# Додаємо корінь проєкту в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app  # Тепер працює правильно

@pytest.fixture
def app() -> Flask:
    flask_app = create_app()
    return flask_app

@pytest.fixture
def client(app: Flask):
    return app.test_client()
