# Browser Traffic Analyzer - Burp Suite Style

A professional HTTP/HTTPS proxy tool for capturing, analyzing, and replaying browser traffic in GitHub Codespaces, with AI-powered analysis using GitHub Copilot.

## 🚀 Features

- **HTTP/HTTPS Proxy Server**: Intercepts all browser traffic
- **Traffic Capture**: Stores all requests and responses in SQLite database
- **Web Interface**: Beautiful, Burp Suite-style UI for viewing traffic
- **AI Analysis**: Copilot-powered security and performance analysis
- **Request Replay**: Replay captured requests for testing
- **Security Scanning**: Automatic detection of common vulnerabilities
- **Performance Metrics**: Track response times and identify bottlenecks
- **Export Functionality**: Export captured traffic as JSON

## 📋 Prerequisites

- Python 3.8+
- GitHub Codespaces (or any Linux environment)
- Modern web browser

## 🛠️ Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the proxy server:
```bash
chmod +x start.sh
./start.sh
```

Or manually:
```bash
python proxy_server.py
```

The tool will start:
- **Web Interface**: http://localhost:8081
- **Proxy Server**: localhost:8080

## 🌐 Browser Configuration

### For Chrome/Chromium:

1. **Using Chrome flags** (recommended for Codespaces):
   ```bash
   google-chrome --proxy-server="localhost:8080" --ignore-certificate-errors
   ```

2. **Using System Settings**:
   - Go to Settings → System → Open proxy settings
   - Configure HTTP/HTTPS proxy: `localhost:8080`

### For Firefox:

1. Go to Settings → Network Settings → Settings
2. Select "Manual proxy configuration"
3. HTTP Proxy: `localhost`, Port: `8080`
4. HTTPS Proxy: `localhost`, Port: `8080`
5. Check "Use this proxy server for all protocols"

### For curl/command line:
```bash
curl -x http://localhost:8080 https://example.com
```

## 🔐 HTTPS Traffic Interception

To intercept HTTPS traffic, you need to install mitmproxy's CA certificate:

1. Configure your browser to use the proxy
2. Visit: http://mitm.it
3. Download and install the certificate for your platform
4. Restart your browser

## 📊 Using the Web Interface

1. Open http://localhost:8081 in your browser
2. Configure your browser's proxy settings (use a different browser or profile)
3. Browse the web normally
4. Watch traffic appear in the interface in real-time

### Features:

- **Request List**: View all captured requests with method, status, and timing
- **Request Details**: Inspect headers, body, and response data
- **Analysis**: Click "Analyze with Copilot" for AI-powered insights
- **Replay**: Resend requests for testing
- **Export**: Save traffic data as JSON

## 🤖 AI-Powered Analysis

The Copilot Agent analyzes requests for:

### Security Issues:
- Sensitive data in URLs
- Missing security headers (HSTS, X-Frame-Options, etc.)
- Insecure HTTP connections
- Basic authentication usage
- SQL injection attempts
- XSS payloads
- CORS misconfigurations

### Performance:
- Slow response times
- Large response sizes
- Missing cache headers
- Lack of compression

### Best Practices:
- API versioning
- HTTP methods usage
- Content negotiation

## 🔧 API Endpoints

### Get All Requests
```bash
GET /api/requests
```

### Get Request Details
```bash
GET /api/requests/{id}
```

### Analyze Request
```bash
POST /api/analyze/{id}
```

### Replay Request
```bash
POST /api/replay/{id}
```

### Clear All Traffic
```bash
DELETE /api/clear
```

## 📁 Database Schema

Traffic is stored in `traffic.db` with the following schema:

```sql
CREATE TABLE requests (
    id INTEGER PRIMARY KEY,
    timestamp REAL,
    method TEXT,
    url TEXT,
    host TEXT,
    path TEXT,
    headers TEXT,
    body TEXT,
    response_status INTEGER,
    response_headers TEXT,
    response_body TEXT,
    duration REAL,
    protocol TEXT,
    analyzed BOOLEAN,
    notes TEXT
);
```

## 🧪 Testing the Agent

Test the AI analysis independently:

```bash
python copilot_agent.py
```

This will analyze recent traffic and provide insights.

## 🔍 Use Cases

1. **Security Testing**: Identify vulnerabilities in web applications
2. **API Development**: Debug and analyze API requests/responses
3. **Performance Optimization**: Find slow endpoints and bottlenecks
4. **Learning**: Understand how web applications communicate
5. **Privacy Analysis**: See what data your browser sends
6. **Debugging**: Inspect failed requests and responses

## 📝 Example Workflow

1. Start the proxy server
2. Configure your browser to use the proxy
3. Visit a website (e.g., https://api.github.com)
4. Open the web interface
5. Select a captured request
6. Click "Analyze with Copilot" to get AI insights
7. Review security issues and recommendations
8. Export results for documentation

## 🛡️ Security Considerations

- This tool intercepts all traffic, including sensitive data
- The database is stored unencrypted - protect `traffic.db`
- Only use on networks and services you own or have permission to test
- The proxy runs on localhost - not accessible from external networks
- HTTPS interception requires installing a CA certificate

## 🤝 Contributing

Feel free to enhance this tool with:
- Additional security checks
- More analysis patterns
- Better UI/UX
- Integration with other security tools
- Custom export formats

## 📄 License

MIT License - use freely for security testing and development.

## 🎯 Roadmap

- [ ] WebSocket traffic capture
- [ ] Advanced filtering and search
- [ ] Custom analysis rules
- [ ] Integration with OWASP ZAP/Burp Suite
- [ ] Request diffing
- [ ] Automated security scans
- [ ] Rate limiting detection
- [ ] Authentication token extraction
- [ ] GraphQL query analysis
- [ ] Real-time collaboration features

## 💡 Tips

- Use the "Refresh" button to manually update the request list
- Filter requests by method, host, or status using browser's search (Ctrl+F)
- Export traffic before clearing to preserve important captures
- Use multiple browser profiles to keep proxy traffic separate
- Check the terminal for detailed proxy logs

## 🐛 Troubleshooting

**Proxy not capturing traffic:**
- Verify browser proxy settings
- Check that port 8080 is not blocked
- Ensure proxy_server.py is running

**HTTPS certificate errors:**
- Install mitmproxy CA certificate from http://mitm.it
- Try using `--ignore-certificate-errors` flag (for testing only)

**Web interface not loading:**
- Check that port 8081 is accessible
- Verify no firewall blocking the port
- Look for errors in terminal output

**Database locked errors:**
- Close other connections to traffic.db
- Restart the proxy server

---

Made with ❤️ for security testing and web development