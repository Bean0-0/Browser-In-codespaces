# Traffic Analyzer Architecture & Workflow

## System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         TRAFFIC ANALYZER                           │
│                    Burp Suite Style Tool with                      │
│                   GitHub Copilot Integration                       │
└────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  CLIENT LAYER (Your Browser/Application)                        │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ HTTP/HTTPS Traffic
             │
             ▼
┌────────────────────────────────────────────────────────────────────┐
│  PROXY LAYER (proxy_server.py)                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  mitmproxy (Port 8080)                                    │     │
│  │  - Intercepts all traffic                                 │     │
│  │  - Captures requests/responses                            │     │
│  │  - Supports HTTP/HTTPS                                    │     │
│  └────────────┬─────────────────────────────────────────────┘     │
└───────────────┼────────────────────────────────────────────────────┘
                │
                │ Store Traffic
                │
                ▼
┌────────────────────────────────────────────────────────────────────┐
│  DATA LAYER (traffic.db)                                           │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  SQLite Database                                          │     │
│  │  - Request/Response storage                               │     │
│  │  - Headers, bodies, metadata                              │     │
│  │  - Timestamps, durations                                  │     │
│  │  - Analysis flags                                         │     │
│  └──────────────────────────────────────────────────────────┘     │
└──────────┬───────────────────────────────┬─────────────────────────┘
           │                               │
           │ Read Traffic                  │ Read Traffic
           │                               │
           ▼                               ▼
┌──────────────────────────┐    ┌────────────────────────────────────┐
│  WEB UI (Port 8081)      │    │  COPILOT API (Port 8082)          │
│  ┌────────────────────┐  │    │  ┌──────────────────────────────┐ │
│  │  aiohttp Web App   │  │    │  │  copilot_api.py              │ │
│  │  - Request list    │  │    │  │  RESTful API Server          │ │
│  │  - Detail view     │  │    │  │                              │ │
│  │  - Real-time UI    │  │    │  │  Endpoints:                  │ │
│  │  - Export tools    │  │    │  │  - Analysis endpoints        │ │
│  └────────────────────┘  │    │  │  - Query endpoints           │ │
└──────────────────────────┘    │  │  - Action endpoints          │ │
                                │  │  - Export endpoints          │ │
                                │  └────────┬─────────────────────┘ │
                                └───────────┼───────────────────────┘
                                            │
                                            │ Uses
                                            │
                                            ▼
                                ┌────────────────────────────────────┐
                                │  AI LAYER (copilot_agent.py)      │
                                │  ┌──────────────────────────────┐ │
                                │  │  CopilotAgent Class          │ │
                                │  │  - Security analysis         │ │
                                │  │  - Performance analysis      │ │
                                │  │  - Pattern detection         │ │
                                │  │  - Recommendations           │ │
                                │  └──────────────────────────────┘ │
                                └────────────────────────────────────┘
```

## Data Flow

### 1. Traffic Capture Flow

```
Browser Request
    │
    ▼
Proxy Intercepts (mitmproxy)
    │
    ├─► Forward to Target Server
    │
    ▼
Receive Response
    │
    ▼
Store in Database
    │
    ├─► Request: method, URL, headers, body
    ├─► Response: status, headers, body
    ├─► Metadata: timestamp, duration, protocol
    │
    ▼
Available for Analysis
```

### 2. Analysis Flow

```
User Request (via API or UI)
    │
    ▼
Copilot API Receives Request
    │
    ▼
Load Data from Database
    │
    ▼
CopilotAgent Analyzes
    │
    ├─► Security Check
    │   ├─► Scan for sensitive data
    │   ├─► Check security headers
    │   ├─► Detect injection attempts
    │   └─► Protocol verification
    │
    ├─► Performance Analysis
    │   ├─► Response time check
    │   ├─► Size analysis
    │   └─► Caching headers
    │
    └─► Best Practices
        ├─► API versioning
        ├─► Compression
        └─► CORS configuration
    │
    ▼
Generate Report
    │
    ▼
Return to User (JSON)
```

### 3. Request Replay Flow

```
User Selects Request
    │
    ▼
API Retrieves Original Request
    │
    ▼
Optional: User Modifies
    │
    ├─► Change headers
    ├─► Modify body
    └─► Update URL
    │
    ▼
Replay Request
    │
    ▼
Capture New Response
    │
    ▼
Store/Compare Results
```

## Component Details

### 1. Proxy Server (`proxy_server.py`)

**Purpose**: Intercept and capture all HTTP/HTTPS traffic

**Key Classes**:
- `TrafficCapture`: mitmproxy addon for capturing traffic
- `ProxyManager`: Manages web interface

**Features**:
- Real-time traffic capture
- SQLite storage
- Web UI with live updates
- Request/response viewing
- Basic analysis triggers

**Technologies**:
- mitmproxy: Proxy server
- aiohttp: Web framework
- SQLite: Database

### 2. Copilot Agent (`copilot_agent.py`)

**Purpose**: AI-powered analysis of captured traffic

**Key Classes**:
- `CopilotAgent`: Main analysis engine
- `RequestAnalysis`: Data class for results

**Analysis Types**:
- **Security**: Vulnerabilities, headers, protocols
- **Performance**: Response times, sizes
- **Best Practices**: Standards compliance

**Detection Capabilities**:
- SQL injection patterns
- XSS attempts
- Sensitive data exposure
- Missing security headers
- Performance bottlenecks
- Protocol issues

### 3. Copilot API (`copilot_api.py`)

**Purpose**: RESTful API for Copilot integration

**Key Classes**:
- `CopilotAPIServer`: API server

**Endpoint Categories**:
- **Analysis**: /copilot/analyze/*
- **Query**: /copilot/query/*
- **Actions**: /copilot/action/*
- **Export**: /copilot/export/*

**Response Format**: JSON

### 4. Database Schema

```sql
CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,              -- Unix timestamp
    method TEXT,                 -- GET, POST, etc.
    url TEXT,                    -- Full URL
    host TEXT,                   -- Hostname
    path TEXT,                   -- URL path
    headers TEXT,                -- JSON string
    body TEXT,                   -- Request body
    response_status INTEGER,     -- HTTP status code
    response_headers TEXT,       -- JSON string
    response_body TEXT,          -- Response body
    duration REAL,               -- Response time (seconds)
    protocol TEXT,               -- http/https
    analyzed BOOLEAN,            -- Analysis flag
    notes TEXT                   -- User notes
);

-- Indexes for performance
CREATE INDEX idx_timestamp ON requests(timestamp);
CREATE INDEX idx_host ON requests(host);
```

## Workflow Examples

### Example 1: Security Testing Workflow

```
1. Start Services
   ./run_all.sh

2. Configure Browser
   Set proxy to localhost:8080

3. Browse Target Application
   Navigate through the app

4. Run Security Scan
   curl -X POST http://localhost:8082/copilot/analyze/security

5. Review Issues
   - Check high-risk requests
   - Review vulnerabilities
   - Read recommendations

6. Fix and Retest
   - Modify requests
   - Replay with fixes
   - Verify improvements

7. Export Report
   curl http://localhost:8082/copilot/export/json > security_report.json
```

### Example 2: API Development Workflow

```
1. Develop API
   Write your API code

2. Start Traffic Analyzer
   ./run_all.sh

3. Test API
   curl -x http://localhost:8080 https://your-api.com/endpoint

4. View in UI
   http://localhost:8081

5. Analyze Performance
   curl -X POST http://localhost:8082/copilot/analyze/performance

6. Optimize
   - Identify slow endpoints
   - Check response sizes
   - Add caching headers

7. Retest
   Replay modified requests

8. Document
   Export as HAR for documentation
```

### Example 3: Continuous Monitoring

```python
import requests
import time

while True:
    # Run analysis every 5 minutes
    security = requests.post(
        'http://localhost:8082/copilot/analyze/security'
    ).json()
    
    if security['total_issues'] > 0:
        # Alert on issues
        send_alert(security)
        
        # Log for review
        log_issues(security)
    
    time.sleep(300)
```

## Integration Points

### 1. Browser Integration
- Configure browser proxy settings
- Install mitmproxy CA certificate (for HTTPS)
- Browse normally

### 2. Command Line Integration
```bash
curl -x http://localhost:8080 https://api.example.com
wget -e use_proxy=yes -e http_proxy=localhost:8080 https://example.com
```

### 3. Python Integration
```python
import requests

proxies = {'http': 'http://localhost:8080', 'https': 'http://localhost:8080'}
response = requests.get('https://example.com', proxies=proxies)
```

### 4. GitHub Copilot Chat
Ask Copilot to analyze traffic:
- "Show me security issues in recent traffic"
- "What are the slowest requests?"
- "Export all POST requests to API"

## Performance Considerations

### Database
- SQLite for simplicity
- Indexes on timestamp and host
- Response body size limited to 1MB
- Auto-cleanup old entries possible

### Proxy
- Async I/O with mitmproxy
- Minimal latency added (~10-50ms)
- HTTPS interception overhead

### API
- Async aiohttp server
- JSON responses
- Optional pagination
- Caching possible

### Scalability
- Current: ~10,000 requests
- For more: Use PostgreSQL
- For distributed: Add Redis cache
- For production: Load balancing

## Security Considerations

### Data Protection
- Database contains sensitive data
- Not encrypted by default
- Keep traffic.db secure
- Add encryption if needed

### Network Security
- Proxy runs on localhost
- Not exposed to internet
- Use firewall rules
- HTTPS interception requires trust

### Best Practices
1. Only test systems you own
2. Delete sensitive data after testing
3. Don't commit traffic.db to git
4. Use separate browser profile
5. Review captured data regularly

## Future Enhancements

### Planned Features
- [ ] WebSocket support
- [ ] Advanced filtering UI
- [ ] Custom analysis rules
- [ ] Request diffing
- [ ] Automated testing scenarios
- [ ] Integration with CI/CD
- [ ] Multi-user support
- [ ] Real-time collaboration

### Integration Opportunities
- OWASP ZAP export
- Burp Suite import/export
- Postman collection export
- OpenAPI spec generation
- GraphQL query analysis
- gRPC support

---

**Built for security testing and API development** 🚀
