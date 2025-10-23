# 🤖 Zybooks Auto-Completion Guide

## Overview

The Zybooks automation tool automatically completes participation activities using authentication tokens captured from your browser traffic. It works by:

1. Extracting your session token from captured HTTP traffic
2. Identifying incomplete activities
3. Sending completion requests to Zybooks API endpoints

## ⚠️ Important Disclaimer

**Educational purposes only.** This tool is for:
- Understanding web API interactions
- Learning about HTTP request/response patterns
- Demonstrating automation techniques

**Use responsibly and ethically.** Check your institution's academic integrity policies.

## Setup

### 1. Capture Traffic

First, browse Zybooks with the proxy running to capture your authentication:

```bash
# Start the traffic analyzer proxy
./bin/start_analyzer.sh

# Configure your browser to use proxy:
#   HTTP Proxy: localhost:8080
#   HTTPS Proxy: localhost:8080
#   Install cert: ./certs/mitmproxy-ca-cert.pem

# Browse to Zybooks and interact with some activities
# This captures your auth token in the database
```

### 2. Verify Captured Data

Check that traffic was captured:

```bash
# View zybooks traffic
python3 bin/traffic_analyzer.py stats --zybooks
python3 bin/traffic_analyzer.py list --zybooks

# Show activity summary
python3 bin/zybooks_autocomplete.py summary
```

### 3. Test Authentication

Verify your auth token was extracted:

```bash
python3 bin/zybooks_autocomplete.py auth
```

## Usage

### Show Activity Summary

Display all activities found in captured traffic:

```bash
python3 bin/zybooks_autocomplete.py summary
```

Output shows:
- Resource IDs
- Part numbers
- Completion status
- Activity URLs

### Auto-Complete (Dry Run)

See what would be completed without making changes:

```bash
python3 bin/zybooks_autocomplete.py auto --dry-run
```

### Auto-Complete All Incomplete Activities

**⚠️ This will actually submit completions:**

```bash
# With default 1 second delay between requests
python3 bin/zybooks_autocomplete.py auto

# With custom delay (slower = more realistic)
python3 bin/zybooks_autocomplete.py auto --delay 2.5
```

### Complete Specific Resources

Complete only specific activity resource IDs:

```bash
python3 bin/zybooks_autocomplete.py complete 115060266 115060274
```

## How It Works

### 1. Authentication Extraction

The script queries the traffic database for recent POST requests to `zyserver.zybooks.com` and extracts:
- **Bearer token** from Authorization header
- **Zybook code** from request body (e.g., "TAMUENGR102Fall2025")

### 2. Activity Detection

Scans captured traffic for URLs matching:
```
https://zyserver.zybooks.com/v1/content_resource/{ID}/activity
```

Parses request bodies to determine:
- Resource ID
- Part number
- Completion status

### 3. Completion Request

Sends POST request with:
```json
{
  "part": 0,
  "complete": true,
  "metadata": "{\"event\":\"animation completely watched\",...}",
  "zybook_code": "TAMUENGR102Fall2025"
}
```

### 4. Response Validation

Checks for success response:
```json
{"success": true}
```

## Command Reference

```bash
# Show help
python3 bin/zybooks_autocomplete.py --help

# Commands:
summary              # Show activity summary from traffic
auto                 # Auto-complete all incomplete activities
complete [IDs...]    # Complete specific resource IDs
auth                 # Extract and display auth token

# Options:
--delay SECONDS      # Delay between requests (default: 1.0)
--dry-run           # Show what would be done without changes
--db PATH           # Path to traffic database (default: data/traffic.db)
```

## Examples

### Basic Workflow

```bash
# 1. Start proxy and browse Zybooks
./bin/start_analyzer.sh

# 2. Check what was captured
python3 bin/zybooks_autocomplete.py summary

# 3. Test with dry run
python3 bin/zybooks_autocomplete.py auto --dry-run

# 4. Auto-complete (if you want to proceed)
python3 bin/zybooks_autocomplete.py auto --delay 2.0
```

### Complete Specific Sections

```bash
# Find resource IDs from summary
python3 bin/zybooks_autocomplete.py summary

# Complete only those resources
python3 bin/zybooks_autocomplete.py complete 115060266 115060274 115060276
```

### Conservative Mode

Use longer delays to avoid detection:

```bash
# 5 second delay between each completion
python3 bin/zybooks_autocomplete.py auto --delay 5.0
```

## Troubleshooting

### "No authenticated zybooks requests found"

**Solution:** Browse Zybooks with the proxy running first. Make sure:
- Proxy is configured in browser
- Certificate is installed
- You've interacted with at least one activity
- Traffic database contains zybooks requests

Check with:
```bash
python3 bin/traffic_analyzer.py list --zybooks --limit 10
```

### "Failed to complete: HTTP 401"

**Problem:** Auth token expired

**Solution:** Recapture traffic with fresh session:
1. Clear traffic database: `python3 bin/traffic_analyzer.py clear`
2. Browse Zybooks again with proxy running
3. Re-run automation

### "Failed to complete: HTTP 403"

**Problem:** Request might be blocked or rate-limited

**Solution:** 
- Use longer delays: `--delay 3.0`
- Complete in smaller batches
- Check if Zybooks has anti-automation measures

## Rate Limiting

To avoid detection and be respectful to servers:

- **Default delay:** 1 second between requests
- **Recommended:** 2-5 seconds for conservative usage
- **Human-like:** Randomize delays (not yet implemented)

## Token Expiration

Auth tokens typically expire after:
- Session timeout (varies)
- Logout
- Password change

If you get 401 errors, recapture traffic with a fresh browser session.

## Advanced: Integration with Traffic Analyzer

Combine with traffic analysis for insights:

```bash
# Filter and analyze zybooks traffic
python3 bin/traffic_analyzer.py stats --zybooks
python3 bin/traffic_analyzer.py search "complete" --zybooks
python3 bin/traffic_analyzer.py export zybooks.har --zybooks

# Then auto-complete
python3 bin/zybooks_autocomplete.py auto
```

## Security Notes

- ⚠️ **Auth tokens are sensitive** - they grant access to your account
- 🔒 Never share your `traffic.db` file (contains tokens)
- 🔑 Tokens are stored in plaintext in the database
- ⏰ Use `clear` command to remove old captured data
- 🚫 Don't commit `traffic.db` to git (already in .gitignore)

## Ethical Considerations

This tool demonstrates:
- ✅ How web APIs work
- ✅ HTTP request/response patterns
- ✅ Authentication mechanisms
- ✅ Automation techniques

**However:**
- ❌ Using it to bypass learning defeats the purpose of coursework
- ❌ May violate academic integrity policies
- ❌ Could be considered cheating depending on context

**Recommended use:**
- Understanding how the platform works
- Automating repetitive tasks you've already completed manually
- Testing and educational purposes only

## Support

For issues:
1. Check `logs/proxy.log` for proxy errors
2. Verify traffic was captured: `python3 bin/traffic_analyzer.py stats --zybooks`
3. Test auth extraction: `python3 bin/zybooks_autocomplete.py auth`
4. Try dry-run mode first: `--dry-run`

## Files

- `bin/zybooks_autocomplete.py` - Main automation script
- `data/traffic.db` - Captured traffic (contains auth tokens)
- `bin/traffic_analyzer.py` - Traffic analysis tool
- `docs/ZYBOOKS_AUTOMATION.md` - This file
