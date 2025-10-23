# 🚀 Quick Reference Guide

## Start/Stop

```bash
# Start proxy
./start_analyzer.sh

# Stop proxy
pkill -f traffic_analyzer
```

## Basic Commands

```bash
# View statistics
./traffic_analyzer.py stats

# List recent requests
./traffic_analyzer.py list

# Show request details
./traffic_analyzer.py show <id>

# Analyze with Copilot
./traffic_analyzer.py analyze

# Search traffic
./traffic_analyzer.py search "query"

# Export to HAR
./traffic_analyzer.py export output.har

# Clear database
./traffic_analyzer.py clear
```

## Filtering

```bash
# Filter by host
./traffic_analyzer.py list --host zybooks.com

# Limit results
./traffic_analyzer.py list --limit 50

# Analyze specific request
./traffic_analyzer.py analyze --id 42
```

## Browser Configuration

**HTTP Proxy:** localhost:8080  
**HTTPS Proxy:** localhost:8080  
**Certificate:** ./certs/mitmproxy-ca-cert.pem

## Copilot Analysis

After running `./traffic_analyzer.py analyze`:

1. Opens temp JSON file with traffic data
2. Shows basic security checks
3. Use in VS Code Chat:
   ```
   @workspace analyze this traffic for security issues
   ```

## Files

- `traffic_analyzer.py` - Main tool
- `traffic.db` - Captured traffic
- `proxy.log` - Proxy logs
- `certs/` - HTTPS certificates

## Get Help

```bash
./traffic_analyzer.py --help
```
