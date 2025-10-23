# 🤖 Zybooks Automation - Quick Reference

## ⚠️ Important

**Educational purposes only.** Use responsibly and check your institution's academic integrity policies.

## Quick Start

```bash
# 1. Start proxy and browse Zybooks
./bin/start_analyzer.sh

# 2. Use interactive menu
./bin/zybooks_quick_start.sh

# OR use commands directly:

# Show summary
python3 bin/zybooks_autocomplete.py summary

# Dry run (safe - no changes)
python3 bin/zybooks_autocomplete.py auto --dry-run

# Auto-complete (CAUTION!)
python3 bin/zybooks_autocomplete.py auto --delay 2.0
```

## Full Documentation

See **[docs/ZYBOOKS_AUTOMATION.md](docs/ZYBOOKS_AUTOMATION.md)** for complete documentation.

## Features

✅ Extracts auth tokens from captured traffic  
✅ Identifies incomplete activities  
✅ Auto-completes participation activities  
✅ Configurable delays (avoid detection)  
✅ Dry-run mode (test without changes)  
✅ Complete specific resources by ID  

## How It Works

1. Proxy captures your Zybooks session with auth token
2. Script extracts token and zybook code from database
3. Queries for incomplete activities
4. Sends completion requests to Zybooks API
5. Respects rate limiting with configurable delays

## Files

- `bin/zybooks_autocomplete.py` - Main automation script
- `bin/zybooks_quick_start.sh` - Interactive menu
- `docs/ZYBOOKS_AUTOMATION.md` - Full documentation
