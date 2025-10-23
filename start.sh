#!/bin/bash

# Traffic Analyzer Startup Script

echo "=================================================="
echo "  Browser Traffic Analyzer - Burp Suite Style"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    touch .deps_installed
    echo "✅ Dependencies installed"
    echo ""
fi

# Kill any existing instances
echo "🧹 Cleaning up old instances..."
pkill -f proxy_server.py 2>/dev/null
sleep 1

# Start the proxy server
echo "🚀 Starting Traffic Analyzer..."
echo ""

python3 proxy_server.py

echo ""
echo "👋 Traffic Analyzer stopped"
