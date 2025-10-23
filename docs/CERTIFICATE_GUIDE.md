# mitmproxy CA Certificate Installation Guide

## 📁 Certificate Files

The mitmproxy CA certificates are located in the `certs/` directory:

- **`mitmproxy-ca-cert.pem`** - For Linux/Unix systems, command line tools
- **`mitmproxy-ca-cert.cer`** - For Windows systems
- **`mitmproxy-ca-cert.p12`** - For iOS/Android devices

## 🌐 Installation Instructions

### Option 1: Easy Method (Recommended)

1. **Start the proxy server** (should already be running on port 8080)

2. **Configure your browser** to use the proxy:
   - HTTP Proxy: `localhost:8080`
   - HTTPS Proxy: `localhost:8080`

3. **Visit the mitmproxy certificate page**:
   - Open: http://mitm.it
   - This will automatically detect your OS
   - Click the appropriate download button for your system

4. **Install the certificate** following the on-screen instructions

### Option 2: Manual Installation

#### 🐧 Linux (Chromium/Chrome)

```bash
# Copy certificate to system trust store
sudo cp certs/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates

# Or for user-only (Chrome/Chromium)
mkdir -p ~/.pki/nssdb
certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n "mitmproxy" -i certs/mitmproxy-ca-cert.pem
```

**Chrome/Chromium via UI**:
1. Settings → Privacy and security → Security
2. Manage certificates → Authorities
3. Import → Select `certs/mitmproxy-ca-cert.pem`
4. Check "Trust this certificate for identifying websites"

#### 🦊 Firefox

1. Settings → Privacy & Security → Certificates
2. View Certificates → Authorities → Import
3. Select `certs/mitmproxy-ca-cert.pem`
4. Check "Trust this CA to identify websites"
5. Click OK

#### 🪟 Windows

1. Double-click `certs/mitmproxy-ca-cert.cer`
2. Click "Install Certificate"
3. Select "Local Machine" → Next
4. Select "Place all certificates in the following store"
5. Browse → Select "Trusted Root Certification Authorities"
6. Finish

Or via PowerShell (as Administrator):
```powershell
Import-Certificate -FilePath "certs\mitmproxy-ca-cert.cer" -CertStoreLocation Cert:\LocalMachine\Root
```

#### 🍎 macOS

```bash
# Add to system keychain
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/mitmproxy-ca-cert.pem

# Or user keychain
security add-trusted-cert -d -r trustRoot -k ~/Library/Keychains/login.keychain certs/mitmproxy-ca-cert.pem
```

**Via Keychain Access**:
1. Double-click `certs/mitmproxy-ca-cert.pem`
2. Add to "System" or "login" keychain
3. Find "mitmproxy" in Keychain Access
4. Double-click → Trust → "Always Trust"

#### 📱 iOS

1. Email yourself `mitmproxy-ca-cert.p12`
2. Open on iOS device
3. Settings → General → VPN & Device Management
4. Install the profile
5. Settings → General → About → Certificate Trust Settings
6. Enable full trust for mitmproxy

#### 🤖 Android

1. Transfer `mitmproxy-ca-cert.p12` to device
2. Settings → Security → Install from storage
3. Select the certificate file
4. Give it a name (e.g., "mitmproxy")
5. Select "VPN and apps" usage

### Option 3: Quick Test (Ignore Certificate Errors)

For testing only, launch Chrome/Chromium with:

```bash
google-chrome --proxy-server="localhost:8080" --ignore-certificate-errors --user-data-dir=/tmp/chrome-proxy
```

⚠️ **Warning**: Only use for testing! This disables security.

## 🧪 Verify Installation

After installing the certificate:

1. **Configure proxy**: `localhost:8080`

2. **Test with HTTPS**:
   ```bash
   curl -x http://localhost:8080 https://www.google.com
   ```

3. **Or visit in browser**:
   - https://www.github.com
   - Should work without certificate warnings

4. **Check in web interface**:
   - http://localhost:8081
   - You should see HTTPS requests captured

## 🔍 Troubleshooting

### Still getting certificate errors?

1. **Restart browser** after installing certificate
2. **Clear SSL cache** in browser settings
3. **Check certificate is installed**:
   - Chrome: chrome://settings/certificates
   - Firefox: about:preferences#privacy → Certificates

### Certificate not trusted?

Make sure you:
- Selected the correct file format for your OS
- Installed to the correct certificate store
- Marked it as trusted for identifying websites

### Can't access http://mitm.it?

1. Verify proxy is running: `./status.sh`
2. Verify browser proxy settings are correct
3. Try: http://mitm.it (not https://)
4. Or use manual installation method above

## 🔐 Security Notes

- **This is a CA certificate** - It allows mitmproxy to intercept HTTPS
- **Only install on systems you control** for testing purposes
- **Remove after testing** if you don't need it anymore
- **Never share the private key** (mitmproxy-ca.pem)

## 🗑️ Remove Certificate

### Linux
```bash
sudo rm /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates --fresh
```

### Windows (PowerShell as Admin)
```powershell
Get-ChildItem Cert:\LocalMachine\Root | Where-Object {$_.Subject -match "mitmproxy"} | Remove-Item
```

### macOS
```bash
sudo security delete-certificate -c "mitmproxy" /Library/Keychains/System.keychain
```

### Firefox
Settings → Privacy & Security → Certificates → View Certificates → Authorities → Delete "mitmproxy"

---

**Need help?** Check the logs: `tail -f proxy.log`
