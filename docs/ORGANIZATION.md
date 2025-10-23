# 📁 Project Organization Guide

## Overview

The project has been reorganized into a clean, professional folder structure that separates concerns and makes it easy to navigate and maintain.

## 📂 Directory Structure

```
Browser-In-codespaces/
│
├── bin/                          # Executable scripts
│   ├── traffic_analyzer.py       # Main CLI tool (18KB)
│   └── start_analyzer.sh         # Startup script
│
├── certs/                        # HTTPS certificates
│   ├── mitmproxy-ca-cert.pem     # PEM format (Firefox, Linux)
│   ├── mitmproxy-ca-cert.cer     # CER format (Windows)
│   └── mitmproxy-ca-cert.p12     # P12 format (macOS Keychain)
│
├── data/                         # Captured traffic and exports
│   ├── traffic.db                # SQLite database with captured requests
│   ├── *.har                     # HAR format exports
│   └── *.json                    # JSON format exports
│
├── docs/                         # Documentation
│   ├── README.md                 # Complete documentation
│   ├── GET_STARTED.md            # Quick start guide
│   ├── QUICK_START.md            # Command reference
│   ├── CERTIFICATE_GUIDE.md      # HTTPS certificate setup
│   ├── CLEANUP_SUMMARY.md        # System simplification summary
│   └── README.old.md             # Previous README (archived)
│
├── logs/                         # Application logs
│   └── proxy.log                 # Proxy server log output
│
├── traffic                       # Convenience wrapper script
├── README.md                     # Main project README
├── requirements.txt              # Python dependencies
└── .gitignore                    # Git ignore rules
```

## 🎯 Folder Purposes

### `/bin` - Executables
Contains all executable scripts and main application code.
- **Purpose:** Centralize executable files
- **Files:** Python scripts, shell scripts
- **Usage:** `./bin/traffic_analyzer.py` or via wrapper

### `/certs` - Certificates
Contains mitmproxy CA certificates for HTTPS interception.
- **Purpose:** Store SSL/TLS certificates
- **Files:** .pem, .cer, .p12 formats
- **Note:** Generated automatically by mitmproxy

### `/data` - Data Files
Contains all captured traffic data and exports.
- **Purpose:** Store captured traffic and exports
- **Files:** SQLite database, HAR/JSON exports
- **Size:** Can grow large with traffic

### `/docs` - Documentation
Contains all documentation files.
- **Purpose:** Keep documentation organized
- **Files:** Markdown documentation files
- **Users:** Developers, end users

### `/logs` - Log Files
Contains application log files.
- **Purpose:** Store runtime logs
- **Files:** .log files
- **Usage:** For debugging and monitoring

## 🚀 Usage Examples

### Using Convenience Wrapper

The `traffic` script in the root is a convenience wrapper:

```bash
./traffic stats          # View statistics
./traffic list           # List requests
./traffic analyze        # Analyze with Copilot
./traffic search "query" # Search traffic
./traffic export out.har # Export to HAR
```

### Using Direct Paths

You can also use direct paths:

```bash
./bin/traffic_analyzer.py stats
./bin/start_analyzer.sh
```

### Working with Data

```bash
# View database
sqlite3 data/traffic.db "SELECT COUNT(*) FROM requests;"

# List exports
ls -lh data/*.har data/*.json

# View logs
tail -f logs/proxy.log
```

## 📝 Configuration Updates

### Path Changes

All scripts have been updated to use the new paths:

**Database:**
- Old: `traffic.db` (root)
- New: `data/traffic.db`

**Logs:**
- Old: `proxy.log` (root)
- New: `logs/proxy.log`

**Scripts:**
- Old: `./traffic_analyzer.py`
- New: `./bin/traffic_analyzer.py` or `./traffic`

## 🔧 .gitignore Updates

The `.gitignore` has been updated to respect the new structure:

```gitignore
# Data files
data/*.db
data/*.har
data/*.json

# Logs
logs/*.log

# Certificates (generated)
certs/*.pem
certs/*.p12
certs/*.cer
```

## 📚 Documentation Locations

| Document | Location | Purpose |
|----------|----------|---------|
| Project Overview | `/README.md` | Quick project intro |
| Full Guide | `/docs/README.md` | Complete documentation |
| Quick Start | `/docs/GET_STARTED.md` | Getting started guide |
| Command Reference | `/docs/QUICK_START.md` | Command cheat sheet |
| Certificate Help | `/docs/CERTIFICATE_GUIDE.md` | HTTPS setup |
| Organization | `/docs/ORGANIZATION.md` | This document |

## 🎨 Benefits

### ✅ Cleaner Root Directory
- Only essential files in root
- Easy to see what's important
- Professional appearance

### ✅ Clear Separation
- Executables in `/bin`
- Data in `/data`
- Docs in `/docs`
- Logs in `/logs`

### ✅ Scalability
- Easy to add more scripts to `/bin`
- Data isolated from code
- Logs don't clutter workspace

### ✅ Maintainability
- Find files faster
- Understand project structure quickly
- Easy to clean up (delete `/data`, `/logs`)

### ✅ Professional
- Follows common conventions
- Similar to standard project layouts
- Easy for others to understand

## 🔄 Migration Notes

If you had scripts or bookmarks using old paths:

**Before:**
```bash
./traffic_analyzer.py stats
python3 traffic_analyzer.py list
cat proxy.log
```

**After:**
```bash
./traffic stats                    # Convenience wrapper
./bin/traffic_analyzer.py stats    # Direct path
cat logs/proxy.log                 # New log location
```

## 🧹 Cleanup

To start fresh:

```bash
# Clear data
rm -rf data/*.db data/*.har data/*.json

# Clear logs
rm -rf logs/*.log

# Regenerate certificates
rm -rf certs/*
# They'll regenerate on next proxy start
```

## 📊 Current Status

```
Database:  data/traffic.db (433 requests)
Logs:      logs/proxy.log
Certs:     certs/ (3 formats)
Docs:      docs/ (6 files)
Scripts:   bin/ (2 files)
```

## 💡 Tips

1. **Use the wrapper:** `./traffic` is easier than `./bin/traffic_analyzer.py`
2. **Check logs:** `tail -f logs/proxy.log` for real-time monitoring
3. **Backup data:** Copy `data/` folder to save important captures
4. **Read docs:** Full documentation in `docs/README.md`

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start proxy | `./bin/start_analyzer.sh` |
| View stats | `./traffic stats` |
| List requests | `./traffic list` |
| Analyze | `./traffic analyze` |
| Search | `./traffic search "query"` |
| Export | `./traffic export file.har` |
| View logs | `tail -f logs/proxy.log` |
| Check data | `ls -lh data/` |
| Read docs | `cat docs/README.md` |

---

**Everything is now organized and ready to use! 🎉**
