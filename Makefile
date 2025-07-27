# Arbitrage Bot Makefile
# Development and deployment commands

.PHONY: help install dev test clean docker build deploy

# Default target
help:
	@echo "🚀 Arbitrage Bot Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install dependencies"
	@echo "  setup       Full setup (install + init-db)"
	@echo ""
	@echo "Development:"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo "  lint        Run code linting"
	@echo "  format      Format code"
	@echo ""
	@echo "Database:"
	@echo "  init-db     Initialize database"
	@echo "  seed-db     Seed database with sample data"
	@echo "  migrate     Run database migrations"
	@echo ""
	@echo "Utilities:"
	@echo "  stats       Show application statistics"
	@echo "  test-exchanges  Test exchange connections"
	@echo "  clear-cache Clear all caches"
	@echo "  backup      Backup database"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run with Docker"
	@echo "  docker-compose  Run with docker-compose"
	@echo ""
	@echo "Deployment:"
	@echo "  build       Build for production"
	@echo "  deploy      Deploy to production"
	@echo "  clean       Clean build artifacts"

# Setup commands
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

setup: install init-db seed-db
	@echo "✅ Setup complete!"

# Development commands
dev:
	@echo "🚀 Starting development server..."
	python run.py

test:
	@echo "🧪 Running tests..."
	pytest

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=. --cov-report=html --cov-report=term

lint:
	@echo "🔍 Running linting..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	@echo "✨ Formatting code..."
	black . --line-length=88
	isort . --profile black

# Database commands
init-db:
	@echo "🗃️ Initializing database..."
	flask init-db

seed-db:
	@echo "🌱 Seeding database..."
	flask seed-db

migrate:
	@echo "🔄 Running migrations..."
	flask db upgrade

# Utility commands
stats:
	@echo "📊 Application statistics:"
	flask stats

test-exchanges:
	@echo "🔌 Testing exchange connections..."
	flask test-exchanges

clear-cache:
	@echo "🗑️ Clearing caches..."
	flask clear-cache

backup:
	@echo "💾 Backing up database..."
	flask backup-db --backup-path=backup_$(shell date +%Y%m%d_%H%M%S).sql

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t arbitrage-bot .

docker-run: docker-build
	@echo "🐳 Running with Docker..."
	docker run -p 5000:5000 --env-file .env arbitrage-bot

docker-compose:
	@echo "🐳 Running with docker-compose..."
	docker-compose up --build

docker-compose-prod:
	@echo "🐳 Running production with docker-compose..."
	docker-compose -f docker-compose.prod.yml up --build -d

# Production commands
build:
	@echo "🏗️ Building for production..."
	pip install -r requirements.txt
	flask init-db

deploy: build
	@echo "🚀 Deploying to production..."
	# Add your deployment commands here
	@echo "Deployment script not configured"

clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/

# Environment setup
env:
	@echo "📝 Creating .env file from template..."
	cp .env.example .env
	@echo "✅ Please edit .env file with your configuration"

# Quick start for new developers
quickstart: env install init-db seed-db
	@echo ""
	@echo "🎉 Quick start complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your API keys (optional)"
	@echo "2. Run 'make dev' to start the development server"
	@echo "3. Open http://127.0.0.1:5000 in your browser"
	@echo ""

# Health check
health:
	@echo "🔍 Checking application health..."
	@curl -s http://127.0.0.1:5000/health | python -m json.tool || echo "❌ Application not running"

# Install development tools
dev-tools:
	@echo "🔧 Installing development tools..."
	pip install black isort flake8 pytest-cov

# Show logs (for development)
logs:
	@echo "📋 Recent application logs:"
	@tail -50 logs/app.log 2>/dev/null || echo "No logs found"

# Performance test
perf-test:
	@echo "⚡ Running performance test..."
	@ab -n 100 -c 10 http://127.0.0.1:5000/api/v1/dashboard || echo "❌ Install apache2-utils for performance testing"