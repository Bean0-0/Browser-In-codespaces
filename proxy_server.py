#!/usr/bin/env python3
"""
Burp Suite-style HTTP/HTTPS Proxy Server
Captures browser traffic for analysis by Copilot
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import base64

from aiohttp import web
from mitmproxy import options
from mitmproxy.tools import dump
from mitmproxy import http, ctx
from mitmproxy.addons import core


class TrafficCapture:
    """Addon for mitmproxy to capture and store HTTP traffic"""
    
    def __init__(self, db_path: str = "traffic.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for traffic storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                analyzed BOOLEAN DEFAULT 0,
                notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON requests(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_host ON requests(host)
        """)
        
        conn.commit()
        conn.close()
    
    def request(self, flow: http.HTTPFlow):
        """Called when a request is received"""
        flow.metadata['start_time'] = time.time()
    
    def response(self, flow: http.HTTPFlow):
        """Called when a response is received"""
        try:
            duration = time.time() - flow.metadata.get('start_time', time.time())
            
            # Extract request data
            request = flow.request
            response = flow.response
            
            # Prepare data for storage
            request_headers = dict(request.headers)
            response_headers = dict(response.headers) if response else {}
            
            # Handle request body
            request_body = ""
            if request.content:
                try:
                    request_body = request.content.decode('utf-8', errors='ignore')
                except:
                    request_body = base64.b64encode(request.content).decode('utf-8')
            
            # Handle response body
            response_body = ""
            if response and response.content:
                try:
                    # Limit response body size
                    if len(response.content) < 1024 * 1024:  # 1MB limit
                        response_body = response.content.decode('utf-8', errors='ignore')
                    else:
                        response_body = f"[Response too large: {len(response.content)} bytes]"
                except:
                    response_body = base64.b64encode(response.content[:10000]).decode('utf-8')
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO requests 
                (timestamp, method, url, host, path, headers, body, 
                 response_status, response_headers, response_body, duration, protocol)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(),
                request.method,
                request.url,
                request.host,
                request.path,
                json.dumps(request_headers),
                request_body,
                response.status_code if response else None,
                json.dumps(response_headers),
                response_body,
                duration,
                request.scheme
            ))
            
            conn.commit()
            conn.close()
            
            ctx.log.info(f"Captured: {request.method} {request.url} - {response.status_code if response else 'No response'}")
        
        except Exception as e:
            ctx.log.error(f"Error storing traffic: {str(e)}")


class ProxyManager:
    """Manages the proxy server and web interface"""
    
    def __init__(self, proxy_port: int = 8080, web_port: int = 8081, db_path: str = "traffic.db"):
        self.proxy_port = proxy_port
        self.web_port = web_port
        self.db_path = db_path
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup web interface routes"""
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/api/requests', self.get_requests)
        self.app.router.add_get('/api/requests/{id}', self.get_request_detail)
        self.app.router.add_post('/api/analyze/{id}', self.analyze_request)
        self.app.router.add_post('/api/replay/{id}', self.replay_request)
        self.app.router.add_delete('/api/clear', self.clear_traffic)
    
    async def index(self, request):
        """Serve the main web interface"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Traffic Analyzer - Burp Suite Style</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .container {
            display: flex;
            height: 100vh;
            flex-direction: column;
        }
        .header {
            background: #252526;
            padding: 15px;
            border-bottom: 1px solid #3e3e42;
        }
        .header h1 {
            color: #569cd6;
            font-size: 24px;
        }
        .controls {
            background: #2d2d30;
            padding: 10px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            gap: 10px;
        }
        button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 3px;
        }
        button:hover {
            background: #1177bb;
        }
        .main {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        .request-list {
            width: 40%;
            border-right: 1px solid #3e3e42;
            overflow-y: auto;
        }
        .request-item {
            padding: 10px;
            border-bottom: 1px solid #3e3e42;
            cursor: pointer;
        }
        .request-item:hover {
            background: #2d2d30;
        }
        .request-item.selected {
            background: #094771;
        }
        .method {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-right: 8px;
        }
        .method.GET { background: #4ec9b0; color: black; }
        .method.POST { background: #ce9178; color: black; }
        .method.PUT { background: #dcdcaa; color: black; }
        .method.DELETE { background: #f48771; color: black; }
        .detail-pane {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 15px;
            border-bottom: 1px solid #3e3e42;
        }
        .tab {
            padding: 8px 16px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
        }
        .tab.active {
            border-bottom-color: #569cd6;
            color: #569cd6;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        pre {
            background: #1e1e1e;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border: 1px solid #3e3e42;
        }
        .info-row {
            margin-bottom: 10px;
            display: flex;
        }
        .info-label {
            color: #569cd6;
            min-width: 120px;
            font-weight: bold;
        }
        .status-200 { color: #4ec9b0; }
        .status-300 { color: #dcdcaa; }
        .status-400 { color: #ce9178; }
        .status-500 { color: #f48771; }
        #stats {
            padding: 10px;
            background: #252526;
            color: #858585;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Traffic Analyzer</h1>
        </div>
        <div id="stats">Loading...</div>
        <div class="controls">
            <button onclick="loadRequests()">🔄 Refresh</button>
            <button onclick="clearTraffic()">🗑️ Clear All</button>
            <button onclick="exportTraffic()">💾 Export</button>
            <span style="margin-left: auto; color: #858585;">
                Proxy: <code>localhost:8080</code>
            </span>
        </div>
        <div class="main">
            <div class="request-list" id="requestList">
                <div style="padding: 20px; text-align: center; color: #858585;">
                    No requests captured yet
                </div>
            </div>
            <div class="detail-pane" id="detailPane">
                <div style="padding: 50px; text-align: center; color: #858585;">
                    Select a request to view details
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedRequestId = null;
        let requests = [];
        
        async function loadRequests() {
            const response = await fetch('/api/requests');
            requests = await response.json();
            displayRequests(requests);
            updateStats(requests);
        }
        
        function displayRequests(requests) {
            const listDiv = document.getElementById('requestList');
            if (requests.length === 0) {
                listDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #858585;">No requests captured yet</div>';
                return;
            }
            
            listDiv.innerHTML = requests.map(req => `
                <div class="request-item ${selectedRequestId === req.id ? 'selected' : ''}" 
                     onclick="selectRequest(${req.id})">
                    <div>
                        <span class="method ${req.method}">${req.method}</span>
                        <span class="status-${Math.floor(req.response_status/100)}00">
                            ${req.response_status || 'N/A'}
                        </span>
                    </div>
                    <div style="margin-top: 5px; font-size: 13px;">${req.host}</div>
                    <div style="margin-top: 3px; font-size: 11px; color: #858585; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${req.path}
                    </div>
                    <div style="margin-top: 3px; font-size: 11px; color: #858585;">
                        ${new Date(req.timestamp * 1000).toLocaleTimeString()} • ${(req.duration * 1000).toFixed(0)}ms
                    </div>
                </div>
            `).join('');
        }
        
        function updateStats(requests) {
            const total = requests.length;
            const methods = {};
            const statuses = {};
            requests.forEach(req => {
                methods[req.method] = (methods[req.method] || 0) + 1;
                const status = Math.floor(req.response_status / 100) + 'xx';
                statuses[status] = (statuses[status] || 0) + 1;
            });
            
            document.getElementById('stats').innerHTML = 
                `Total Requests: ${total} | ` +
                Object.entries(methods).map(([m, c]) => `${m}: ${c}`).join(' | ');
        }
        
        async function selectRequest(id) {
            selectedRequestId = id;
            displayRequests(requests);
            
            const response = await fetch(`/api/requests/${id}`);
            const req = await response.json();
            
            const detailPane = document.getElementById('detailPane');
            detailPane.innerHTML = `
                <div class="tabs">
                    <div class="tab active" onclick="switchTab(0)">Request</div>
                    <div class="tab" onclick="switchTab(1)">Response</div>
                    <div class="tab" onclick="switchTab(2)">Headers</div>
                    <div class="tab" onclick="switchTab(3)">Actions</div>
                </div>
                
                <div class="tab-content active">
                    <div class="info-row">
                        <div class="info-label">Method:</div>
                        <div>${req.method}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">URL:</div>
                        <div>${req.url}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Protocol:</div>
                        <div>${req.protocol}</div>
                    </div>
                    <h3 style="margin-top: 20px; margin-bottom: 10px;">Request Body</h3>
                    <pre>${req.body || '(empty)'}</pre>
                </div>
                
                <div class="tab-content">
                    <div class="info-row">
                        <div class="info-label">Status:</div>
                        <div class="status-${Math.floor(req.response_status/100)}00">${req.response_status}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Duration:</div>
                        <div>${(req.duration * 1000).toFixed(2)}ms</div>
                    </div>
                    <h3 style="margin-top: 20px; margin-bottom: 10px;">Response Body</h3>
                    <pre>${req.response_body || '(empty)'}</pre>
                </div>
                
                <div class="tab-content">
                    <h3 style="margin-bottom: 10px;">Request Headers</h3>
                    <pre>${JSON.stringify(JSON.parse(req.headers), null, 2)}</pre>
                    <h3 style="margin-top: 20px; margin-bottom: 10px;">Response Headers</h3>
                    <pre>${JSON.stringify(JSON.parse(req.response_headers), null, 2)}</pre>
                </div>
                
                <div class="tab-content">
                    <button onclick="analyzeRequest(${id})">🤖 Analyze with Copilot</button>
                    <button onclick="replayRequest(${id})">▶️ Replay Request</button>
                    <div id="analysisResult" style="margin-top: 20px;"></div>
                </div>
            `;
        }
        
        function switchTab(index) {
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            tabs.forEach((tab, i) => {
                tab.classList.toggle('active', i === index);
            });
            contents.forEach((content, i) => {
                content.classList.toggle('active', i === index);
            });
        }
        
        async function analyzeRequest(id) {
            const resultDiv = document.getElementById('analysisResult');
            resultDiv.innerHTML = '<p>Analyzing with Copilot...</p>';
            
            const response = await fetch(`/api/analyze/${id}`, { method: 'POST' });
            const result = await response.json();
            
            resultDiv.innerHTML = `
                <h3>Analysis Results</h3>
                <pre>${JSON.stringify(result, null, 2)}</pre>
            `;
        }
        
        async function replayRequest(id) {
            if (confirm('Replay this request?')) {
                const response = await fetch(`/api/replay/${id}`, { method: 'POST' });
                const result = await response.json();
                alert(result.message);
            }
        }
        
        async function clearTraffic() {
            if (confirm('Clear all captured traffic?')) {
                await fetch('/api/clear', { method: 'DELETE' });
                loadRequests();
            }
        }
        
        function exportTraffic() {
            const data = JSON.stringify(requests, null, 2);
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `traffic_${Date.now()}.json`;
            a.click();
        }
        
        // Auto-refresh every 2 seconds
        setInterval(loadRequests, 2000);
        
        // Initial load
        loadRequests();
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def get_requests(self, request):
        """Get all captured requests"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, method, url, host, path, 
                   response_status, duration, protocol
            FROM requests
            ORDER BY timestamp DESC
            LIMIT 1000
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        requests = [dict(row) for row in rows]
        return web.json_response(requests)
    
    async def get_request_detail(self, request):
        """Get detailed information about a specific request"""
        request_id = request.match_info['id']
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return web.json_response(dict(row))
        else:
            return web.json_response({'error': 'Request not found'}, status=404)
    
    async def analyze_request(self, request):
        """Analyze a request (placeholder for Copilot integration)"""
        request_id = request.match_info['id']
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return web.json_response({'error': 'Request not found'}, status=404)
        
        req_data = dict(row)
        
        # This is where you'd integrate with Copilot
        analysis = {
            "summary": f"{req_data['method']} request to {req_data['url']}",
            "status": req_data['response_status'],
            "security_notes": [],
            "performance": {
                "duration_ms": req_data['duration'] * 1000,
                "rating": "good" if req_data['duration'] < 1 else "slow"
            },
            "suggestions": [
                "Request captured successfully",
                "Use Copilot agent mode for deeper analysis"
            ]
        }
        
        # Check for common security issues
        headers = json.loads(req_data['headers'])
        if 'authorization' in [h.lower() for h in headers.keys()]:
            analysis['security_notes'].append("Contains authorization header")
        
        # Mark as analyzed
        cursor.execute("UPDATE requests SET analyzed = 1 WHERE id = ?", (request_id,))
        conn.commit()
        conn.close()
        
        return web.json_response(analysis)
    
    async def replay_request(self, request):
        """Replay a captured request"""
        request_id = request.match_info['id']
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return web.json_response({'error': 'Request not found'}, status=404)
        
        # In a real implementation, you'd replay the request here
        return web.json_response({
            'message': f'Request {request_id} replay initiated',
            'url': row['url'],
            'method': row['method']
        })
    
    async def clear_traffic(self, request):
        """Clear all captured traffic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM requests")
        conn.commit()
        conn.close()
        
        return web.json_response({'message': 'Traffic cleared'})


async def start_web_server(manager: ProxyManager):
    """Start the web interface server"""
    runner = web.AppRunner(manager.app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', manager.web_port)
    await site.start()
    print(f"🌐 Web interface running on http://localhost:{manager.web_port}")


async def start_proxy_async(proxy_port: int = 8080, db_path: str = "traffic.db"):
    """Start the mitmproxy server asynchronously"""
    opts = options.Options(listen_host='0.0.0.0', listen_port=proxy_port)
    
    master = dump.DumpMaster(
        opts,
        with_termlog=True,
        with_dumper=False,
    )
    
    master.addons.add(TrafficCapture(db_path))
    
    print(f"🔌 Proxy server running on port {proxy_port}")
    print(f"📊 Configure your browser to use proxy: localhost:{proxy_port}")
    
    try:
        await master.run()
    finally:
        master.shutdown()


def start_proxy(proxy_port: int = 8080, db_path: str = "traffic.db"):
    """Start the mitmproxy server"""
    try:
        asyncio.run(start_proxy_async(proxy_port, db_path))
    except KeyboardInterrupt:
        print("\n🛑 Proxy server stopped")
    except Exception as e:
        print(f"❌ Proxy server error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    import threading
    
    proxy_port = 8080
    web_port = 8081
    db_path = "traffic.db"
    
    print("\n" + "="*60)
    print("🚀 Traffic Analyzer Started!")
    print("="*60)
    print(f"📊 Web Interface: http://localhost:{web_port}")
    print(f"🔌 Proxy Server: localhost:{proxy_port}")
    print("\n📝 Configure your browser proxy settings:")
    print(f"   HTTP Proxy: localhost:{proxy_port}")
    print(f"   HTTPS Proxy: localhost:{proxy_port}")
    print("\n⚠️  For HTTPS traffic, you may need to install mitmproxy's CA certificate")
    print("   Visit http://mitm.it after configuring the proxy")
    print("="*60 + "\n")
    
    # Start web server first
    manager = ProxyManager(proxy_port, web_port, db_path)
    
    async def run_web_server():
        await start_web_server(manager)
        # Keep running
        while True:
            await asyncio.sleep(3600)
    
    # Run web server in a thread
    def web_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_web_server())
        except KeyboardInterrupt:
            pass
    
    web_t = threading.Thread(target=web_thread, daemon=True)
    web_t.start()
    
    # Give web server time to start
    time.sleep(2)
    
    # Start proxy in main thread (blocking)
    try:
        start_proxy(proxy_port, db_path)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
