#!/bin/bash

# All-in-One Setup and Start Script

echo "=================================================="
echo "  Traffic Analyzer - Complete Setup"
echo "=================================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found"

# Install dependencies
if [ ! -f ".deps_installed" ]; then
    echo ""
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        touch .deps_installed
        echo "✅ Dependencies installed"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "=================================================="
echo "  🚀 Starting All Services"
echo "=================================================="
echo ""

# Kill any existing processes
pkill -f proxy_server.py 2>/dev/null
pkill -f copilot_api.py 2>/dev/null
sleep 1

# Start proxy server in background
echo "🔌 Starting Proxy Server (port 8080)..."
python3 proxy_server.py > proxy.log 2>&1 &
PROXY_PID=$!
echo "   PID: $PROXY_PID"
sleep 2

# Start Copilot API in background
echo "🤖 Starting Copilot API Server (port 8082)..."
python3 copilot_api.py > copilot_api.log 2>&1 &
API_PID=$!
echo "   PID: $API_PID"
sleep 2

# Check if services started
if ps -p $PROXY_PID > /dev/null && ps -p $API_PID > /dev/null; then
    echo ""
    echo "=================================================="
    echo "  ✅ All Services Started!"
    echo "=================================================="
    echo ""
    echo "📊 Web Interface:    http://localhost:8081"
    echo "🔌 Proxy Server:     localhost:8080"
    echo "🤖 Copilot API:      http://localhost:8082"
    echo ""
    echo "📝 Logs:"
    echo "   Proxy:     tail -f proxy.log"
    echo "   API:       tail -f copilot_api.log"
    echo ""
    echo "🧪 Run Demo:"
    echo "   python3 demo.py"
    echo ""
    echo "🧪 Test Proxy:"
    echo "   python3 test_proxy.py"
    echo ""
    echo "🛑 Stop Services:"
    echo "   kill $PROXY_PID $API_PID"
    echo ""
    echo "=================================================="
    echo ""
    
    # Save PIDs
    echo "$PROXY_PID" > .proxy.pid
    echo "$API_PID" > .api.pid
    
    echo "✨ Ready to capture traffic!"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:8081 to see the web interface"
    echo "  2. Configure your browser proxy to localhost:8080"
    echo "  3. Or run: python3 demo.py for a complete demo"
    echo ""
else
    echo ""
    echo "❌ Failed to start services"
    echo "Check logs for details:"
    echo "  cat proxy.log"
    echo "  cat copilot_api.log"
    exit 1
fi

# Wait and keep script running
echo "Press Ctrl+C to stop all services..."
trap "echo ''; echo 'Stopping services...'; kill $PROXY_PID $API_PID 2>/dev/null; rm -f .proxy.pid .api.pid; echo 'Done!'" EXIT INT TERM

wait
