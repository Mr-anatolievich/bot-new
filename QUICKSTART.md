# 🚀 Quick Start Guide

Get your Arbitrage Bot up and running in **less than 5 minutes**!

---

## 🎯 Option 1: Super Quick Setup (Recommended)

### 1. **Automated Setup Script**
```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

**That's it!** The script will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Setup configuration files
- ✅ Initialize database
- ✅ Test the installation

### 2. **Start the Application**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Start development server
python run.py
```

### 3. **Access the Platform**
- **Frontend**: http://127.0.0.1:5000
- **API**: http://127.0.0.1:5000/api/v1
- **Health**: http://127.0.0.1:5000/health

---

## 🎯 Option 2: Docker (Easiest)

### 1. **Quick Docker Run**
```bash
# Copy environment file
cp .env.example .env

# Run with Docker Compose
docker-compose up --build
```

### 2. **Access the Platform**
- **Frontend**: http://localhost
- **API**: http://localhost/api/v1

---

## 🎯 Option 3: Manual Setup

### 1. **Prerequisites Check**
```bash
# Check Python version (3.8+ required)
python3 --version

# Check pip
pip3 --version
```

### 2. **Environment Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. **Configuration**
```bash
# Create environment file
cp .env.example .env

# Edit configuration (optional)
nano .env  # Add your API keys here
```

### 4. **Database Setup**
```bash
# Initialize database
flask init-db

# Seed with sample data (optional)
flask seed-db
```

### 5. **Start Application**
```bash
python run.py
```

---

## 🎯 Option 4: Using Makefile

```bash
# Complete setup
make quickstart

# Start development server
make dev

# Run tests
make test

# Check application stats
make stats
```

---

## 🔧 Configuration (Optional)

### **API Keys Setup**
Edit `.env` file to add your exchange API keys:

```bash
# Binance (optional)
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here

# Bybit (optional) 
BYBIT_API_KEY=your_key_here
BYBIT_API_SECRET=your_secret_here

# Other exchanges...
```

> **Note**: API keys are **optional** for testing. The app works with public APIs.

---

## 🎉 First Steps After Setup

### 1. **Check Exchange Connections**
```bash
flask test-exchanges
```

### 2. **View Application Statistics**
```bash
flask stats
```

### 3. **Find Arbitrage Opportunities**
```bash
flask find-arbitrage --min-spread 0.1
```

### 4. **Test API Endpoints**
```bash
# Dashboard data
curl http://127.0.0.1:5000/api/v1/dashboard

# Arbitrage opportunities
curl http://127.0.0.1:5000/api/v1/arbitrage

# Exchange status
curl http://127.0.0.1:5000/api/v1/exchanges
```

---

## 🎮 Features to Explore

### **Web Interface**
- 📊 **Dashboard**: Real-time statistics and charts
- 🔄 **Arbitrage**: Live arbitrage opportunities
- 🪙 **Tokens**: Price comparison across exchanges
- 🌐 **Networks**: Withdrawal fees and networks

### **API Endpoints**
- `/api/v1/dashboard` - Dashboard data
- `/api/v1/arbitrage` - Arbitrage opportunities
- `/api/v1/tokens` - Token prices and data
- `/api/v1/networks` - Network fees and info
- `/api/v1/exchanges` - Exchange status

### **CLI Commands**
- `flask stats` - Application statistics
- `flask test-exchanges` - Test connections
- `flask find-arbitrage` - Find opportunities
- `flask clear-cache` - Clear data cache

---

## 🛠️ Development Commands

### **Common Tasks**
```bash
# View help
make help

# Run tests
make test

# Check code quality
make lint

# Clear all caches
make clear-cache

# Backup database
make backup
```

### **Development Server**
```bash
# Start with auto-reload
python run.py

# Or with make
make dev
```

---

## 🚨 Troubleshooting

### **Common Issues**

1. **Port 5000 already in use**
   ```bash
   # Change port in .env file
   PORT=8000
   ```

2. **Python not found**
   ```bash
   # Install Python 3.8+
   # On Ubuntu: sudo apt install python3 python3-pip
   # On macOS: brew install python
   ```

3. **Virtual environment issues**
   ```bash
   # Remove and recreate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Database errors**
   ```bash
   # Reset database
   flask drop-db
   flask init-db
   ```

5. **Exchange connection errors**
   ```bash
   # Test specific exchange
   flask test-exchanges
   
   # Clear cache and retry
   flask clear-cache
   ```

### **Getting Help**
- Check logs: `tail -f logs/app.log`
- Test API: `curl http://127.0.0.1:5000/health`
- View stats: `flask stats`

---

## 🎯 What's Next?

1. **🔑 Add API Keys**: Edit `.env` file for enhanced features
2. **📊 Explore Dashboard**: Check real-time arbitrage data
3. **🔧 Customize Settings**: Adjust `config/settings.py`
4. **🚀 Deploy**: Use Docker for production deployment
5. **📈 Monitor**: Set up alerts and monitoring

---

## 🌟 Pro Tips

- **Development**: Use `make dev` for auto-reload
- **Testing**: Run `make test` before deploying
- **Monitoring**: Check `make stats` regularly
- **Performance**: Use `make clear-cache` if data seems stale
- **Backup**: Run `make backup` before major changes

---

**🎉 You're all set! Start exploring profitable arbitrage opportunities!**

**Need help?** Check the [README.md](README.md) for detailed documentation.