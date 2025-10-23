# 🌐 HTTP Traffic Analyzer# Browser Traffic Analyzer - Burp Suite Style



A **Burp Suite-style** HTTP/HTTPS traffic analysis tool that captures browser traffic and integrates with **GitHub Copilot** for AI-powered security and performance analysis.A professional HTTP/HTTPS proxy tool for capturing, analyzing, and replaying browser traffic in GitHub Codespaces, with AI-powered analysis using GitHub Copilot.



## 🎯 What It Does## 🚀 Features



- 🔍 **Captures** all HTTP/HTTPS traffic from your browser- **HTTP/HTTPS Proxy Server**: Intercepts all browser traffic

- 💾 **Stores** traffic in SQLite database for analysis- **Traffic Capture**: Stores all requests and responses in SQLite database

- 🤖 **Analyzes** with GitHub Copilot CLI for security insights- **Web Interface**: Beautiful, Burp Suite-style UI for viewing traffic

- 📊 **Exports** to HAR format for external tools- **AI Analysis**: Copilot-powered security and performance analysis

- 🔒 **Detects** security vulnerabilities and issues- **Request Replay**: Replay captured requests for testing

- **Security Scanning**: Automatic detection of common vulnerabilities

## 🚀 Quick Start- **Performance Metrics**: Track response times and identify bottlenecks

- **Export Functionality**: Export captured traffic as JSON

### 1. Start the Proxy

## 📋 Prerequisites

```bash

./start_analyzer.sh- Python 3.8+

```- GitHub Codespaces (or any Linux environment)

- Modern web browser

This will:

- Start the proxy server on port **8080**## 🛠️ Installation

- Create the traffic database

- Show you the certificate location1. Install dependencies:

```bash

### 2. Configure Your Browserpip install -r requirements.txt

```

**Firefox:**

- Settings → Network Settings → Manual proxy configuration2. Start the proxy server:

- HTTP Proxy: `localhost` Port: `8080````bash

- HTTPS Proxy: `localhost` Port: `8080`chmod +x start.sh

- ✅ Also use this proxy for HTTPS./start.sh

```

**Chrome:**

```bashOr manually:

google-chrome --proxy-server="localhost:8080"```bash

```python proxy_server.py

```

### 3. Install HTTPS Certificate

The tool will start:

For HTTPS interception:- **Web Interface**: http://localhost:8081

```bash- **Proxy Server**: localhost:8080

# Certificate is at:

./certs/mitmproxy-ca-cert.pem## 🌐 Browser Configuration



# Firefox: Settings → Certificates → Import### For Chrome/Chromium:

# Chrome: Settings → Security → Manage Certificates → Import

```1. **Using Chrome flags** (recommended for Codespaces):

   ```bash

See `CERTIFICATE_GUIDE.md` for detailed instructions.   google-chrome --proxy-server="localhost:8080" --ignore-certificate-errors

   ```

### 4. Browse the Web

2. **Using System Settings**:

Your traffic is now being captured! Visit any website.   - Go to Settings → System → Open proxy settings

   - Configure HTTP/HTTPS proxy: `localhost:8080`

### 5. Analyze Traffic

### For Firefox:

```bash

# View statistics1. Go to Settings → Network Settings → Settings

./traffic_analyzer.py stats2. Select "Manual proxy configuration"

3. HTTP Proxy: `localhost`, Port: `8080`

# List recent requests4. HTTPS Proxy: `localhost`, Port: `8080`

./traffic_analyzer.py list5. Check "Use this proxy server for all protocols"



# Show specific request### For curl/command line:

./traffic_analyzer.py show 42```bash

curl -x http://localhost:8080 https://example.com

# Analyze with Copilot```

./traffic_analyzer.py analyze

## 🔐 HTTPS Traffic Interception

# Search traffic

./traffic_analyzer.py search "api_key"To intercept HTTPS traffic, you need to install mitmproxy's CA certificate:



# Export to HAR1. Configure your browser to use the proxy

./traffic_analyzer.py export traffic.har2. Visit: http://mitm.it

```3. Download and install the certificate for your platform

4. Restart your browser

---

## 📊 Using the Web Interface

## 📚 Commands Reference

1. Open http://localhost:8081 in your browser

### Proxy Management2. Configure your browser's proxy settings (use a different browser or profile)

3. Browse the web normally

```bash4. Watch traffic appear in the interface in real-time

# Start proxy

./traffic_analyzer.py proxy### Features:



# Or use the helper script- **Request List**: View all captured requests with method, status, and timing

./start_analyzer.sh- **Request Details**: Inspect headers, body, and response data

- **Analysis**: Click "Analyze with Copilot" for AI-powered insights

# Stop proxy- **Replay**: Resend requests for testing

pkill -f traffic_analyzer- **Export**: Save traffic data as JSON

```

## 🤖 AI-Powered Analysis

### Traffic Viewing

The Copilot Agent analyzes requests for:

```bash

# View statistics### Security Issues:

./traffic_analyzer.py stats- Sensitive data in URLs

- Missing security headers (HSTS, X-Frame-Options, etc.)

# List recent requests (default: 10)- Insecure HTTP connections

./traffic_analyzer.py list- Basic authentication usage

- SQL injection attempts

# List more requests- XSS payloads

./traffic_analyzer.py list --limit 50- CORS misconfigurations



# Filter by host### Performance:

./traffic_analyzer.py list --host zybooks.com- Slow response times

- Large response sizes

# Show request details- Missing cache headers

./traffic_analyzer.py show <request_id>- Lack of compression

```

### Best Practices:

### Analysis with Copilot- API versioning

- HTTP methods usage

```bash- Content negotiation

# Analyze recent traffic (last 20 requests)

./traffic_analyzer.py analyze## 🔧 API Endpoints



# Analyze specific request### Get All Requests

./traffic_analyzer.py analyze --id 42```bash

GET /api/requests

# This will:```

# - Show traffic summary

# - Run basic security checks### Get Request Details

# - Create JSON file for Copilot analysis```bash

# - Give you instructions to use Copilot ChatGET /api/requests/{id}

``````



**Using with GitHub Copilot:**### Analyze Request

```bash

After running analyze, you can:POST /api/analyze/{id}

```

1. **In VS Code Chat:**

   ```### Replay Request

   @workspace analyze the traffic data for security issues```bash

   ```POST /api/replay/{id}

```

2. **Open the generated JSON:**

   The command creates a temp file - open it and ask Copilot:### Clear All Traffic

   - "Are there any security vulnerabilities in this traffic?"```bash

   - "What endpoints are being called?"DELETE /api/clear

   - "Are there any sensitive data leaks?"```

   - "Suggest performance improvements"

## 📁 Database Schema

### Search & Export

Traffic is stored in `traffic.db` with the following schema:

```bash

# Search through traffic```sql

./traffic_analyzer.py search "login"CREATE TABLE requests (

./traffic_analyzer.py search "api_key"    id INTEGER PRIMARY KEY,

./traffic_analyzer.py search "password"    timestamp REAL,

    method TEXT,

# Export to HAR format    url TEXT,

./traffic_analyzer.py export output.har    host TEXT,

    path TEXT,

# Export specific host    headers TEXT,

./traffic_analyzer.py export zybooks.har --host zybooks.com    body TEXT,

    response_status INTEGER,

# Export limited results    response_headers TEXT,

./traffic_analyzer.py export recent.har --limit 100    response_body TEXT,

```    duration REAL,

    protocol TEXT,

### Database Management    analyzed BOOLEAN,

    notes TEXT

```bash);

# Clear all captured traffic```

./traffic_analyzer.py clear

```## 🧪 Testing the Agent



---Test the AI analysis independently:



## 🎯 Use Cases```bash

python copilot_agent.py

### 1. Security Testing```



```bashThis will analyze recent traffic and provide insights.

# Capture traffic from your app

./traffic_analyzer.py proxy &## 🔍 Use Cases



# Browse your application1. **Security Testing**: Identify vulnerabilities in web applications

# Then analyze for security issues2. **API Development**: Debug and analyze API requests/responses

./traffic_analyzer.py analyze3. **Performance Optimization**: Find slow endpoints and bottlenecks

4. **Learning**: Understand how web applications communicate

# Search for sensitive data5. **Privacy Analysis**: See what data your browser sends

./traffic_analyzer.py search "password"6. **Debugging**: Inspect failed requests and responses

./traffic_analyzer.py search "api_key"

./traffic_analyzer.py search "token"## 📝 Example Workflow

```

1. Start the proxy server

### 2. API Debugging2. Configure your browser to use the proxy

3. Visit a website (e.g., https://api.github.com)

```bash4. Open the web interface

# List API requests5. Select a captured request

./traffic_analyzer.py list --host api.example.com6. Click "Analyze with Copilot" to get AI insights

7. Review security issues and recommendations

# Show specific API call8. Export results for documentation

./traffic_analyzer.py show 123

## 🛡️ Security Considerations

# Export for Postman/Insomnia

./traffic_analyzer.py export api_calls.har --host api.example.com- This tool intercepts all traffic, including sensitive data

```- The database is stored unencrypted - protect `traffic.db`

- Only use on networks and services you own or have permission to test

### 3. Performance Analysis- The proxy runs on localhost - not accessible from external networks

- HTTPS interception requires installing a CA certificate

```bash

# View statistics including average duration## 🤝 Contributing

./traffic_analyzer.py stats

Feel free to enhance this tool with:

# Analyze for performance issues- Additional security checks

./traffic_analyzer.py analyze- More analysis patterns

- Better UI/UX

# Export slow requests for analysis- Integration with other security tools

./traffic_analyzer.py list --limit 100- Custom export formats

```

## 📄 License

### 4. Learning & Research

MIT License - use freely for security testing and development.

```bash

# Capture traffic from a website## 🎯 Roadmap

# Analyze how it works

./traffic_analyzer.py list --host example.com- [ ] WebSocket traffic capture

- [ ] Advanced filtering and search

# Export for detailed study- [ ] Custom analysis rules

./traffic_analyzer.py export learning.har --host example.com- [ ] Integration with OWASP ZAP/Burp Suite

```- [ ] Request diffing

- [ ] Automated security scans

---- [ ] Rate limiting detection

- [ ] Authentication token extraction

## 📖 Example Workflow- [ ] GraphQL query analysis

- [ ] Real-time collaboration features

### Analyzing a Website's Security

## 💡 Tips

```bash

# 1. Start proxy- Use the "Refresh" button to manually update the request list

./start_analyzer.sh- Filter requests by method, host, or status using browser's search (Ctrl+F)

- Export traffic before clearing to preserve important captures

# 2. Configure browser to use proxy (localhost:8080)- Use multiple browser profiles to keep proxy traffic separate

- Check the terminal for detailed proxy logs

# 3. Visit the website

## 🐛 Troubleshooting

# 4. View what was captured

./traffic_analyzer.py stats**Proxy not capturing traffic:**

./traffic_analyzer.py list- Verify browser proxy settings

- Check that port 8080 is not blocked

# 5. Analyze with Copilot- Ensure proxy_server.py is running

./traffic_analyzer.py analyze

**HTTPS certificate errors:**

# 6. This shows:- Install mitmproxy CA certificate from http://mitm.it

#    - Traffic summary- Try using `--ignore-certificate-errors` flag (for testing only)

#    - Security issues (missing HSTS, CSP, etc.)

#    - Creates JSON file for deeper Copilot analysis**Web interface not loading:**

- Check that port 8081 is accessible

# 7. Open VS Code Chat and ask:- Verify no firewall blocking the port

#    "@workspace analyze the traffic data - what security issues do you see?"- Look for errors in terminal output



# 8. Export for external tools**Database locked errors:**

./traffic_analyzer.py export website_traffic.har- Close other connections to traffic.db

```- Restart the proxy server



------



## 🔧 Technical DetailsMade with ❤️ for security testing and web development

### Architecture

- **Proxy**: mitmproxy for HTTP/HTTPS interception
- **Storage**: SQLite database (`traffic.db`)
- **Analysis**: GitHub Copilot CLI integration
- **Export**: HAR (HTTP Archive) format

### Database Schema

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

### Files

- `traffic_analyzer.py` - Main CLI tool (proxy + analysis)
- `start_analyzer.sh` - Quick start script
- `traffic.db` - SQLite database with captured traffic
- `certs/` - mitmproxy CA certificates
- `proxy.log` - Proxy server logs

---

## 🤖 Copilot Integration

This tool is designed to work seamlessly with GitHub Copilot:

### Built-in Analysis

When you run `./traffic_analyzer.py analyze`, it:
1. Extracts recent traffic data
2. Performs basic security checks
3. Creates a JSON file with traffic details
4. Provides instructions for Copilot analysis

### Using Copilot Chat

After running analyze:

```
@workspace I have HTTP traffic data. Can you:
1. Identify security vulnerabilities
2. Check for data leaks
3. Analyze API usage patterns
4. Suggest performance improvements
```

### Example Prompts

- "Analyze this traffic for SQL injection attempts"
- "Are there any unencrypted sensitive data transmissions?"
- "What authentication methods are being used?"
- "Show me all POST requests with large payloads"
- "Are there any CORS misconfigurations?"

---

## 🛡️ Security & Privacy

⚠️ **Important Notes:**

- This tool captures **ALL** traffic through the proxy
- Traffic is stored **unencrypted** in `traffic.db`
- Be careful with sensitive data (passwords, tokens, etc.)
- Only use on **networks/systems you control**
- Use for **educational/testing purposes** only

### Best Practices

1. **Don't** use on public WiFi
2. **Don't** capture other people's traffic
3. **Do** clear database after testing: `./traffic_analyzer.py clear`
4. **Do** secure your traffic.db file
5. **Do** use for your own security testing

---

## 📝 Requirements

```bash
pip install mitmproxy aiohttp
```

Or use the `start_analyzer.sh` script which installs dependencies automatically.

---

## 🐛 Troubleshooting

### Proxy won't start

```bash
# Check if port 8080 is in use
lsof -i :8080

# Kill existing process
pkill -f traffic_analyzer

# Try again
./start_analyzer.sh
```

### HTTPS not working

- Make sure certificate is installed in your browser
- See `CERTIFICATE_GUIDE.md` for detailed instructions
- Restart browser after installing certificate

### No traffic captured

```bash
# Check proxy is running
ps aux | grep traffic_analyzer

# Check browser proxy settings
# Should be: localhost:8080 for both HTTP and HTTPS

# Check database
./traffic_analyzer.py stats
```

### Database locked

```bash
# Close any other tools accessing the database
# Or restart the proxy
pkill -f traffic_analyzer
./start_analyzer.sh
```

---

## 🎓 Learn More

- **HAR Format**: [HTTP Archive Specification](http://www.softwareishard.com/blog/har-12-spec/)
- **mitmproxy**: [Documentation](https://docs.mitmproxy.org/)
- **GitHub Copilot**: [Copilot Chat](https://docs.github.com/en/copilot)

---

## 📄 License

For educational and security testing purposes only.

---

**Happy analyzing! 🚀🔍**
