#!/bin/bash
# Simple startup script for Traffic Analyzer

echo "🚀 HTTP Traffic Analyzer - Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Python dependencies are installed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q mitmproxy aiohttp
    echo "✅ Dependencies installed"
else
    source .venv/bin/activate
fi

# Start the proxy in the background
echo "🌐 Starting proxy server on port 8080..."
cd "$(dirname "$0")/.."
python3 bin/traffic_analyzer.py proxy > logs/proxy.log 2>&1 &
PROXY_PID=$!
echo $PROXY_PID > .proxy.pid

sleep 2

if ps -p $PROXY_PID > /dev/null; then
    echo "✅ Proxy server running (PID: $PROXY_PID)"
    echo ""
    echo "📊 Configure your browser:"
    echo "   HTTP Proxy: localhost:8080"
    echo "   HTTPS Proxy: localhost:8080"
    echo ""
    echo "📜 Install certificate:"
    echo "   ./certs/mitmproxy-ca-cert.pem"
    echo ""
    echo "💻 Available Commands:"
    echo "   ./bin/traffic_analyzer.py stats         # View statistics"
    echo "   ./bin/traffic_analyzer.py list          # List requests"
    echo "   ./bin/traffic_analyzer.py analyze       # Analyze with Copilot"
    echo "   ./bin/traffic_analyzer.py --help        # See all commands"
    echo ""
    echo "🛑 To stop: kill $PROXY_PID"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "❌ Failed to start proxy server"
    echo "Check proxy.log for errors"
    exit 1
fi
