#!/bin/bash

echo "======================================================"
echo "  🔍 TRAFFIC ANALYZER - SYSTEM STATUS"
echo "======================================================"
echo ""

# Check if services are running
PROXY_PID=$(pgrep -f "python3 proxy_server.py")
API_PID=$(pgrep -f "python3 copilot_api.py")

if [ -n "$PROXY_PID" ]; then
    echo "✅ Proxy Server:     RUNNING (PID: $PROXY_PID)"
else
    echo "❌ Proxy Server:     NOT RUNNING"
fi

if [ -n "$API_PID" ]; then
    echo "✅ Copilot API:      RUNNING (PID: $API_PID)"
else
    echo "❌ Copilot API:      NOT RUNNING"
fi

echo ""

# Check web interface
if curl -s http://localhost:8081 > /dev/null 2>&1; then
    echo "✅ Web Interface:    http://localhost:8081 (UP)"
else
    echo "❌ Web Interface:    http://localhost:8081 (DOWN)"
fi

# Check API
if curl -s http://localhost:8082/copilot/query/methods > /dev/null 2>&1; then
    echo "✅ API Endpoint:     http://localhost:8082 (UP)"
else
    echo "❌ API Endpoint:     http://localhost:8082 (DOWN)"
fi

echo ""

# Check database
if [ -f "traffic.db" ]; then
    SIZE=$(du -h traffic.db | cut -f1)
    COUNT=$(sqlite3 traffic.db "SELECT COUNT(*) FROM requests" 2>/dev/null || echo "0")
    echo "✅ Database:         traffic.db ($SIZE, $COUNT requests)"
else
    echo "ℹ️  Database:         No traffic captured yet"
fi

echo ""
echo "======================================================"
echo ""
echo "📋 Quick Commands:"
echo "  View web interface:  Open http://localhost:8081"
echo "  Run demo:            python3 demo.py"
echo "  Test proxy:          python3 test_proxy.py"
echo "  Stop services:       pkill -f 'proxy_server|copilot_api'"
echo ""
echo "💡 Need help? Check README.md or QUICK_REFERENCE.md"
echo ""
