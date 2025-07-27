#!/bin/bash

# Arbitrage Bot Setup Script
# Quick setup for development environment

set -e  # Exit on any error

echo "🚀 Arbitrage Bot Setup Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."

    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    elif command -v pip &> /dev/null; then
        print_success "pip found"
    else
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."

    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."

    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_success "Virtual environment activated (Windows)"
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Create .env file
create_env_file() {
    print_status "Setting up environment configuration..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success ".env file created from template"
            print_warning "Please edit .env file with your configuration"
        else
            print_warning ".env.example not found, creating basic .env file"
            cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
HOST=127.0.0.1
PORT=5000
DATABASE_URL=sqlite:///arbitrage.db
CACHE_DURATION=3600
MIN_ARBITRAGE_SPREAD=0.1
EOF
            print_success "Basic .env file created"
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Initialize database
init_database() {
    print_status "Initializing database..."

    if command -v flask &> /dev/null; then
        flask init-db
        print_success "Database initialized"

        # Ask if user wants to seed the database
        echo ""
        read -p "Do you want to seed the database with sample data? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            flask seed-db
            print_success "Database seeded with sample data"
        fi
    else
        print_warning "Flask CLI not available, skipping database initialization"
        print_status "You can initialize the database later with: flask init-db"
    fi
}

# Test installation
test_installation() {
    print_status "Testing installation..."

    if command -v python &> /dev/null; then
        python -c "
try:
    from app import create_app
    app = create_app('testing')
    print('✅ Application imports successfully')
except Exception as e:
    print(f'❌ Application import failed: {e}')
    exit(1)
"
        print_success "Installation test passed"
    else
        print_warning "Could not test installation"
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys (optional for testing)"
    echo "2. Activate virtual environment:"
    echo "   source venv/bin/activate  # Linux/Mac"
    echo "   venv\\Scripts\\activate     # Windows"
    echo "3. Start the development server:"
    echo "   python run.py"
    echo "   # or"
    echo "   make dev"
    echo "4. Open your browser to http://127.0.0.1:5000"
    echo ""
    echo "Additional commands:"
    echo "  make help           - Show all available commands"
    echo "  make test           - Run tests"
    echo "  make test-exchanges - Test exchange connections"
    echo "  make stats          - Show application statistics"
    echo ""
    echo "For API documentation, visit: http://127.0.0.1:5000/api/v1"
    echo ""
}

# Main setup process
main() {
    echo "Starting setup process..."
    echo ""

    # Check prerequisites
    check_python
    check_pip

    # Setup environment
    create_venv
    activate_venv
    install_dependencies

    # Configure application
    create_env_file
    init_database

    # Test installation
    test_installation

    # Show completion message
    show_next_steps
}

# Handle command line arguments
case "${1:-setup}" in
    "setup"|"")
        main
        ;;
    "clean")
        print_status "Cleaning up..."
        rm -rf venv/
        rm -f .env
        rm -f *.db
        rm -rf __pycache__/
        rm -rf .pytest_cache/
        print_success "Cleanup complete"
        ;;
    "test")
        print_status "Running quick test..."
        activate_venv
        python -c "from app import create_app; print('✅ App creation test passed')"
        ;;
    "help")
        echo "Arbitrage Bot Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup (default) - Full setup process"
        echo "  clean          - Remove all generated files"
        echo "  test           - Quick installation test"
        echo "  help           - Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac