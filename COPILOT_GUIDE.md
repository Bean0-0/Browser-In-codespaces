# Copilot Agent Mode Integration Guide

## Overview

This guide shows how to use the Traffic Analyzer with GitHub Copilot in agent mode to automatically analyze captured traffic and respond with intelligent insights.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser   │─────▶│ Proxy Server │─────▶│  Database   │
│             │      │  (port 8080) │      │ (traffic.db)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │ Web Interface│      │Copilot Agent│
                     │  (port 8081) │      │             │
                     └──────────────┘      └─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │ Copilot API │
                                           │ (port 8082) │
                                           └─────────────┘
```

## Running All Components

### Terminal 1: Start Proxy Server
```bash
python3 proxy_server.py
```
This starts:
- Proxy server on port 8080
- Web interface on port 8081

### Terminal 2: Start Copilot API Server
```bash
python3 copilot_api.py
```
This starts the API server on port 8082

### Terminal 3: Test Traffic Capture
```bash
python3 test_proxy.py
```

## Using the Copilot API

### 1. Analyze a Specific Request

```bash
# Get the request ID from the web interface or database
curl -X POST http://localhost:8082/copilot/analyze/request/1
```

Response:
```json
{
  "success": true,
  "request_id": 1,
  "analysis": {
    "summary": "GET request to http://httpbin.org/get ✅ succeeded (200) in 234ms...",
    "security_score": 85.0,
    "vulnerabilities": [
      "Missing HSTS header",
      "🔓 Insecure HTTP protocol"
    ],
    "recommendations": [
      "💡 Consider adding cache headers for GET requests"
    ],
    "insights": {
      "method": "GET",
      "status_code": 200,
      "duration_ms": 234.5,
      "has_auth": false,
      "content_type": "application/json"
    }
  }
}
```

### 2. Analyze Session Traffic

```bash
curl -X POST http://localhost:8082/copilot/analyze/session \
  -H "Content-Type: application/json" \
  -d '{"limit": 50}'
```

### 3. Security Scan

```bash
curl -X POST http://localhost:8082/copilot/analyze/security
```

Response:
```json
{
  "success": true,
  "total_issues": 15,
  "unique_issues": 5,
  "high_risk_requests": [
    {
      "request_id": 3,
      "score": 60.0,
      "issues": [
        "🔓 Insecure HTTP protocol",
        "⚠️ Sensitive data detected in URL"
      ]
    }
  ],
  "all_issues": [
    "Missing HSTS header",
    "🔓 Insecure HTTP protocol",
    "Missing X-Content-Type-Options header"
  ]
}
```

### 4. Performance Analysis

```bash
curl -X POST http://localhost:8082/copilot/analyze/performance
```

### 5. Query Requests

```bash
# Get all POST requests
curl "http://localhost:8082/copilot/query/requests?method=POST"

# Get all 404 errors
curl "http://localhost:8082/copilot/query/requests?status=404"

# Get requests to specific host
curl "http://localhost:8082/copilot/query/requests?host=github.com"
```

### 6. Replay Request

```bash
curl -X POST http://localhost:8082/copilot/action/replay/1
```

### 7. Modify and Replay

```bash
curl -X POST http://localhost:8082/copilot/action/modify/1 \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.github.com/users/octocat",
    "headers": {
      "Authorization": "Bearer NEW_TOKEN",
      "User-Agent": "Traffic-Analyzer/1.0"
    }
  }'
```

### 8. Export Traffic

```bash
# Export as JSON
curl http://localhost:8082/copilot/export/json > traffic.json

# Export as HAR (HTTP Archive)
curl http://localhost:8082/copilot/export/har > traffic.har
```

## Copilot Agent Workflow Examples

### Example 1: Automated Security Analysis

```python
import requests

# Step 1: Capture some traffic (browse normally)
# Step 2: Run security scan
response = requests.post('http://localhost:8082/copilot/analyze/security')
scan_results = response.json()

# Step 3: Copilot analyzes results
for request_info in scan_results['high_risk_requests']:
    request_id = request_info['request_id']
    
    # Get detailed analysis
    analysis = requests.post(
        f'http://localhost:8082/copilot/analyze/request/{request_id}'
    ).json()
    
    print(f"Request #{request_id}:")
    print(f"  Security Score: {analysis['analysis']['security_score']}/100")
    print(f"  Issues: {', '.join(analysis['analysis']['vulnerabilities'])}")
    print(f"  Recommendations: {', '.join(analysis['analysis']['recommendations'])}")
```

### Example 2: Performance Monitoring

```python
import requests
import time

while True:
    # Get performance metrics
    perf = requests.post(
        'http://localhost:8082/copilot/analyze/performance'
    ).json()
    
    metrics = perf['metrics']
    
    # Alert on performance issues
    if metrics['avg_response_time_ms'] > 1000:
        print(f"⚠️ High average response time: {metrics['avg_response_time_ms']}ms")
        
        # Show slowest requests
        for req in perf['slowest_requests'][:3]:
            print(f"  - {req['method']} {req['url']}: {req['duration']*1000:.0f}ms")
    
    time.sleep(60)  # Check every minute
```

### Example 3: API Testing Automation

```python
import requests

# Query all API requests
api_requests = requests.get(
    'http://localhost:8082/copilot/query/requests',
    params={'host': 'api.example.com'}
).json()

for req in api_requests['requests']:
    # Analyze each request
    analysis = requests.post(
        f"http://localhost:8082/copilot/analyze/request/{req['id']}"
    ).json()
    
    # Check for issues
    if analysis['analysis']['security_score'] < 80:
        print(f"⚠️ Security issue in {req['method']} {req['path']}")
        
        # Modify request to fix issues
        modified = requests.post(
            f"http://localhost:8082/copilot/action/modify/{req['id']}",
            json={
                'headers': {
                    'X-Security-Token': 'SECURE_TOKEN',
                    'Content-Type': 'application/json'
                }
            }
        ).json()
        
        print(f"✅ Modified request ready to replay")
```

## Integration with GitHub Copilot Chat

You can ask Copilot to analyze traffic directly:

**User**: "Analyze the security of recent traffic"

**Copilot**: 
```python
import requests

# Get security scan results
scan = requests.post('http://localhost:8082/copilot/analyze/security').json()

print(f"Found {scan['total_issues']} security issues")
print(f"High risk requests: {len(scan['high_risk_requests'])}")

# Detailed analysis of high-risk requests
for req in scan['high_risk_requests']:
    analysis = requests.post(
        f"http://localhost:8082/copilot/analyze/request/{req['request_id']}"
    ).json()
    
    print(f"\nRequest #{req['request_id']}:")
    print(analysis['analysis']['summary'])
```

**User**: "Show me all POST requests with errors"

**Copilot**:
```python
import requests

# Query failed POST requests
failed_posts = requests.get(
    'http://localhost:8082/copilot/query/requests',
    params={'method': 'POST'}
).json()

for req in failed_posts['requests']:
    if req['response_status'] >= 400:
        print(f"{req['method']} {req['url']} - Status: {req['response_status']}")
        print(f"  Body: {req['body'][:100]}...")
```

## Advanced Use Cases

### 1. Continuous Security Monitoring

```python
import requests
import time
from datetime import datetime

def monitor_security():
    while True:
        # Run security scan every 5 minutes
        scan = requests.post('http://localhost:8082/copilot/analyze/security').json()
        
        if scan['total_issues'] > 0:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] ⚠️ Security Alert: {scan['total_issues']} issues found")
            
            # Log high-risk requests
            with open('security_log.txt', 'a') as f:
                f.write(f"\n[{timestamp}] Security Issues:\n")
                for issue in scan['all_issues']:
                    f.write(f"  - {issue}\n")
        
        time.sleep(300)  # 5 minutes

monitor_security()
```

### 2. API Response Diffing

```python
import requests
import json

# Capture baseline request
baseline_id = 1
baseline = requests.get(f'http://localhost:8082/copilot/query/requests/{baseline_id}').json()

# Replay and compare
for i in range(5):
    result = requests.post(f'http://localhost:8082/copilot/action/replay/{baseline_id}').json()
    
    # Compare responses
    # (In production, you'd capture the new response and compare)
    print(f"Replay {i+1}: {result['message']}")
```

### 3. Traffic Pattern Analysis

```python
import requests

# Get all hosts
hosts = requests.get('http://localhost:8082/copilot/query/hosts').json()

print("Traffic Distribution:")
for host in hosts['hosts'][:10]:
    print(f"  {host['host']}: {host['count']} requests")

# Get methods distribution
methods = requests.get('http://localhost:8082/copilot/query/methods').json()

print("\nHTTP Methods:")
for method in methods['methods']:
    print(f"  {method['method']}: {method['count']} requests")
```

## Best Practices

1. **Always analyze before replaying**: Check security and correctness first
2. **Use filters**: Query specific requests instead of analyzing everything
3. **Export regularly**: Save traffic data for later analysis
4. **Monitor performance**: Track response times and identify bottlenecks
5. **Secure your data**: The database contains sensitive traffic data
6. **Rate limit replays**: Don't overwhelm target servers

## Troubleshooting

**API returns 500 error**:
- Check if database exists and is accessible
- Verify traffic has been captured
- Check Python console for errors

**No traffic captured**:
- Verify proxy is running on port 8080
- Check browser proxy settings
- Ensure browser is configured correctly

**Analysis seems incorrect**:
- Check if request data is complete
- Verify database integrity
- Review copilot_agent.py logic

## Next Steps

1. Build custom analysis rules
2. Integrate with CI/CD pipelines
3. Create automated test scenarios
4. Build dashboards with the data
5. Train models on traffic patterns
6. Add webhook notifications for alerts

---

Happy analyzing! 🚀
