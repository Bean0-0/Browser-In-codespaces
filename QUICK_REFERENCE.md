# Traffic Analyzer - Quick Reference Card

## 🚀 Quick Start (3 Commands)

```bash
# 1. Start everything
./run_all.sh

# 2. Open web interface
# Visit: http://localhost:8081

# 3. Run demo (in new terminal)
python3 demo.py
```

## 📡 Ports

| Service | Port | URL |
|---------|------|-----|
| Proxy Server | 8080 | N/A (configure in browser) |
| Web Interface | 8081 | http://localhost:8081 |
| Copilot API | 8082 | http://localhost:8082 |

## 🌐 Configure Browser Proxy

### Chrome/Chromium
```bash
google-chrome --proxy-server="localhost:8080"
```

### Firefox
Settings → Network → Manual proxy → HTTP Proxy: `localhost:8080`

### curl
```bash
curl -x http://localhost:8080 https://example.com
```

## 🤖 Copilot API Endpoints

### Analysis
```bash
# Analyze specific request
POST /copilot/analyze/request/{id}

# Analyze session
POST /copilot/analyze/session

# Security scan
POST /copilot/analyze/security

# Performance analysis
POST /copilot/analyze/performance
```

### Queries
```bash
# Query requests
GET /copilot/query/requests?method=GET&status=200

# Get hosts
GET /copilot/query/hosts

# Get methods
GET /copilot/query/methods
```

### Actions
```bash
# Replay request
POST /copilot/action/replay/{id}

# Modify and replay
POST /copilot/action/modify/{id}
```

### Export
```bash
# Export as JSON
GET /copilot/export/json

# Export as HAR
GET /copilot/export/har
```

## 💡 Common Tasks

### 1. Capture Traffic
```bash
# Start services
./run_all.sh

# In another terminal, browse or:
curl -x http://localhost:8080 https://api.github.com
```

### 2. Analyze Security
```bash
curl -X POST http://localhost:8082/copilot/analyze/security | jq
```

### 3. Check Performance
```bash
curl -X POST http://localhost:8082/copilot/analyze/performance | jq
```

### 4. Find Specific Requests
```bash
# All POST requests
curl "http://localhost:8082/copilot/query/requests?method=POST" | jq

# Failed requests (4xx/5xx)
curl "http://localhost:8082/copilot/query/requests?status=404" | jq

# Requests to specific host
curl "http://localhost:8082/copilot/query/requests?host=github.com" | jq
```

### 5. Export Data
```bash
# Export as JSON
curl http://localhost:8082/copilot/export/json > traffic.json

# Export as HAR
curl http://localhost:8082/copilot/export/har > traffic.har
```

## 🧪 Testing

### Test Proxy
```bash
python3 test_proxy.py
```

### Run Complete Demo
```bash
python3 demo.py
```

### Test Copilot Agent
```bash
python3 copilot_agent.py
```

## 📂 Files

| File | Purpose |
|------|---------|
| `proxy_server.py` | Main proxy server + web UI |
| `copilot_agent.py` | AI analysis engine |
| `copilot_api.py` | RESTful API for Copilot |
| `demo.py` | Complete demo script |
| `test_proxy.py` | Quick proxy test |
| `run_all.sh` | Start all services |
| `traffic.db` | SQLite database (auto-created) |

## 🔧 Troubleshooting

### Proxy not working?
```bash
# Check if running
ps aux | grep proxy_server

# Check logs
tail -f proxy.log

# Restart
./run_all.sh
```

### API not responding?
```bash
# Check if running
ps aux | grep copilot_api

# Check logs
tail -f copilot_api.log

# Test connection
curl http://localhost:8082/copilot/query/methods
```

### HTTPS errors?
```bash
# Install mitmproxy CA certificate
# 1. Configure proxy in browser
# 2. Visit: http://mitm.it
# 3. Install certificate for your OS
```

### Clear all data
```bash
rm traffic.db
```

## 📊 Example Analysis with Copilot

### In Python
```python
import requests

# Security scan
scan = requests.post('http://localhost:8082/copilot/analyze/security')
print(scan.json())

# Performance check
perf = requests.post('http://localhost:8082/copilot/analyze/performance')
print(perf.json())

# Query requests
reqs = requests.get('http://localhost:8082/copilot/query/requests?limit=10')
for req in reqs.json()['requests']:
    print(f"{req['method']} {req['url']} - {req['response_status']}")
```

### With curl + jq
```bash
# Show security issues
curl -s -X POST http://localhost:8082/copilot/analyze/security | \
  jq '.all_issues[]'

# Show slowest requests
curl -s -X POST http://localhost:8082/copilot/analyze/performance | \
  jq '.slowest_requests[] | "\(.method) \(.url): \(.duration*1000)ms"'

# Count by status code
curl -s 'http://localhost:8082/copilot/query/requests' | \
  jq '[.requests[].response_status] | group_by(.) | map({status: .[0], count: length})'
```

## 🎯 Use Cases

1. **Security Testing**: Find vulnerabilities in web apps
2. **API Development**: Debug API calls
3. **Performance**: Identify slow endpoints
4. **Learning**: Understand HTTP traffic
5. **Privacy**: See what data apps send
6. **Debugging**: Inspect request/response

## 📚 Documentation

- Full README: `README.md`
- Copilot Guide: `COPILOT_GUIDE.md`
- This card: `QUICK_REFERENCE.md`

## 🛑 Stop Services

```bash
# If started with run_all.sh
# Press Ctrl+C

# Or manually
kill $(cat .proxy.pid) $(cat .api.pid)

# Or kill all
pkill -f proxy_server.py
pkill -f copilot_api.py
```

---

**Pro Tip**: Keep this file open while working! 📌
