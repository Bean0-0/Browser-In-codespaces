#!/usr/bin/env python3
"""
HTTP Traffic Analyzer - Burp Suite Style with Copilot CLI Integration
Simplified version that uses GitHub Copilot CLI for analysis
"""

import asyncio
import json
import sqlite3
import time
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import threading

from mitmproxy import options
from mitmproxy.tools import dump
from mitmproxy import http
from mitmproxy.addons import core


class TrafficCapture:
    """Addon for mitmproxy to capture and store HTTP traffic"""
    
    def __init__(self, db_path: str = "data/traffic.db"):
        self.db_path = db_path
        self.only_zybooks = False
        # initialize
        self.init_database()
        self.request_count = 0
    
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
        
        conn.commit()
        conn.close()
    
    def request(self, flow: http.HTTPFlow):
        """Called when a request is received"""
        flow.metadata["start_time"] = time.time()
    
    def response(self, flow: http.HTTPFlow):
        """Called when a response is received"""
        duration = time.time() - flow.metadata.get("start_time", time.time())
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Parse request
            req = flow.request
            resp = flow.response
            
            headers = json.dumps(dict(req.headers))
            body = req.content.decode('utf-8', errors='ignore') if req.content else ""
            
            resp_headers = json.dumps(dict(resp.headers)) if resp else "{}"
            resp_body = resp.content.decode('utf-8', errors='ignore') if resp and resp.content else ""
            resp_status = resp.status_code if resp else 0
            
            cursor.execute("""
                INSERT INTO requests 
                (timestamp, method, url, host, path, headers, body, 
                 response_status, response_headers, response_body, duration, protocol)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(),
                req.method,
                req.url,
                req.host,
                req.path,
                headers,
                body,
                resp_status,
                resp_headers,
                resp_body,
                duration,
                req.scheme
            ))
            
            conn.commit()
            self.request_count += 1
            
            # Print to console
            status_color = "✅" if resp_status < 400 else "❌"
            print(f"{status_color} [{resp_status}] {req.method} {req.url[:80]}")
            
        except Exception as e:
            print(f"Error storing request: {e}")
        finally:
            conn.close()


class TrafficAnalyzerCLI:
    """CLI tool for analyzing captured traffic using Copilot"""
    
    def __init__(self, db_path: str = "data/traffic.db"):
        self.db_path = db_path
        self.only_zybooks = False
    
    def get_stats(self):
        """Get traffic statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Apply optional host filtering
        clause, params = self._host_clause_and_params(None)

        cursor.execute(f"SELECT COUNT(*) FROM requests {clause}", tuple(params))
        total = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(DISTINCT host) FROM requests {clause}", tuple(params))
        unique_hosts = cursor.fetchone()[0]

        cursor.execute(f"SELECT method, COUNT(*) as count FROM requests {clause} GROUP BY method", tuple(params))
        methods = cursor.fetchall()

        cursor.execute(f"SELECT AVG(duration) FROM requests {clause}", tuple(params))
        avg_duration = cursor.fetchone()[0] or 0

        conn.close()
        
        print(f"\n📊 Traffic Statistics")
        print(f"━━━━━━━━━━━━━━━━━━━━")
        print(f"Total Requests: {total}")
        print(f"Unique Hosts: {unique_hosts}")
        print(f"Avg Duration: {avg_duration*1000:.2f}ms")
        print(f"\nMethods:")
        for method, count in methods:
            print(f"  {method}: {count}")
    
    def list_requests(self, limit: int = 10, host: Optional[str] = None):
        """List recent requests"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        clause, params = self._host_clause_and_params(host)
        # Add limit at the end of params
        params_with_limit = params + [limit]
        cursor.execute(f"SELECT * FROM requests {clause} ORDER BY timestamp DESC LIMIT ?", tuple(params_with_limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        print(f"\n📋 Recent Requests ({len(rows)})")
        print(f"{'ID':<6} {'Method':<8} {'Status':<8} {'Duration':<10} {'URL'}")
        print("━" * 100)
        
        for row in rows:
            url = row['url'][:60] + "..." if len(row['url']) > 60 else row['url']
            duration = f"{row['duration']*1000:.0f}ms"
            status = str(row['response_status'])
            print(f"{row['id']:<6} {row['method']:<8} {status:<8} {duration:<10} {url}")
    
    def show_request(self, request_id: int):
        """Show detailed information about a specific request"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Respect zybooks-only filtering if set
        if self.only_zybooks:
            cursor.execute("SELECT * FROM requests WHERE id = ? AND host LIKE ?", (request_id, "%zybooks%"))
        else:
            cursor.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print(f"❌ Request {request_id} not found")
            return
        
        print(f"\n🔍 Request Details (ID: {request_id})")
        print("━" * 80)
        print(f"Method:   {row['method']}")
        print(f"URL:      {row['url']}")
        print(f"Host:     {row['host']}")
        print(f"Status:   {row['response_status']}")
        print(f"Duration: {row['duration']*1000:.2f}ms")
        print(f"Protocol: {row['protocol']}")
        print(f"Time:     {datetime.fromtimestamp(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📤 Request Headers:")
        headers = json.loads(row['headers'])
        for key, value in list(headers.items())[:10]:
            print(f"  {key}: {value[:60]}...")
        
        if row['body']:
            print(f"\n📦 Request Body ({len(row['body'])} bytes):")
            print(f"  {row['body'][:200]}...")
        
        print(f"\n📥 Response Headers:")
        resp_headers = json.loads(row['response_headers'])
        for key, value in list(resp_headers.items())[:10]:
            print(f"  {key}: {value[:60]}...")
        
        if row['response_body']:
            print(f"\n📦 Response Body ({len(row['response_body'])} bytes):")
            print(f"  {row['response_body'][:200]}...")
    
    def analyze_with_copilot(self, request_id: Optional[int] = None):
        """Analyze traffic using GitHub Copilot CLI"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if request_id:
            # If zybooks-only is set, ensure the specific request matches
            if self.only_zybooks:
                cursor.execute("SELECT * FROM requests WHERE id = ? AND host LIKE ?", (request_id, "%zybooks%"))
            else:
                cursor.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
            rows = [cursor.fetchone()]
            context = f"Analyzing request ID {request_id}"
        else:
            clause, params = self._host_clause_and_params(None)
            cursor.execute(f"SELECT * FROM requests {clause} ORDER BY timestamp DESC LIMIT 20", tuple(params))
            rows = cursor.fetchall()
            context = "Analyzing last 20 requests"
        
        conn.close()
        
        if not rows or not rows[0]:
            print("❌ No requests found")
            return
        
        # Build analysis prompt
        analysis_data = []
        for row in rows:
            analysis_data.append({
                'id': row['id'],
                'method': row['method'],
                'url': row['url'],
                'status': row['response_status'],
                'duration_ms': row['duration'] * 1000,
                'headers': json.loads(row['headers']),
                'response_headers': json.loads(row['response_headers'])
            })
        
        # Create a temporary file with the data
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(analysis_data, f, indent=2)
            temp_file = f.name
        
        print(f"\n🤖 {context}")
        print("━" * 80)
        print(f"Data prepared in: {temp_file}")
        print(f"\nTo analyze with GitHub Copilot, you can:")
        print(f"1. Open the file in VS Code: code {temp_file}")
        print(f"2. Ask Copilot: 'Analyze this HTTP traffic for security issues'")
        print(f"3. Use Copilot Chat: '@workspace analyze this traffic data'")
        print(f"\nOr use the interactive mode below:")
        print("━" * 80)
        
        # Show summary
        print("\n📊 Traffic Summary:")
        methods = {}
        hosts = set()
        status_codes = {}
        
        for row in rows:
            method = row['method']
            methods[method] = methods.get(method, 0) + 1
            hosts.add(row['host'])
            status = row['response_status']
            status_codes[status] = status_codes.get(status, 0) + 1
        
        print(f"  Requests: {len(rows)}")
        print(f"  Unique Hosts: {len(hosts)}")
        print(f"  Methods: {', '.join([f'{k}({v})' for k,v in methods.items()])}")
        print(f"  Status Codes: {', '.join([f'{k}({v})' for k,v in status_codes.items()])}")
        
        # Basic security checks
        print("\n🔒 Quick Security Check:")
        security_issues = []
        
        for row in rows:
            headers = json.loads(row['response_headers'])
            
            # Check for missing security headers
            if 'strict-transport-security' not in [h.lower() for h in headers.keys()]:
                security_issues.append(f"⚠️  Request {row['id']}: Missing HSTS header")
            
            if 'x-frame-options' not in [h.lower() for h in headers.keys()]:
                security_issues.append(f"⚠️  Request {row['id']}: Missing X-Frame-Options")
            
            if 'content-security-policy' not in [h.lower() for h in headers.keys()]:
                security_issues.append(f"⚠️  Request {row['id']}: Missing CSP header")
        
        if security_issues:
            for issue in security_issues[:5]:
                print(f"  {issue}")
            if len(security_issues) > 5:
                print(f"  ... and {len(security_issues) - 5} more issues")
        else:
            print("  ✅ No obvious security issues detected")
    
    def search(self, query: str):
        """Search through captured traffic"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build search clause and include host filtering if required
        search_clause = "(url LIKE ? OR body LIKE ? OR response_body LIKE ? )"
        search_params = [f"%{query}%", f"%{query}%", f"%{query}%"]

        host_clause, host_params = self._host_clause_and_params(None)

        if host_clause:
            full_clause = f"WHERE {search_clause} AND " + host_clause[len('WHERE '):]
            params = search_params + host_params
        else:
            full_clause = f"WHERE {search_clause}"
            params = search_params

        cursor.execute(f"SELECT * FROM requests {full_clause} ORDER BY timestamp DESC LIMIT 50", tuple(params))
        
        rows = cursor.fetchall()
        conn.close()
        
        print(f"\n🔍 Search Results for '{query}' ({len(rows)} found)")
        print("━" * 80)
        
        for row in rows:
            print(f"ID {row['id']}: {row['method']} {row['url'][:60]}")

    def _host_clause_and_params(self, host: Optional[str]):
        """Return SQL WHERE clause and parameters based on host filter and zybooks-only flag.

        host: explicit host substring to match (from CLI --host). If None, only the zybooks-only
        setting is applied. Returns a tuple (clause, params) where clause includes leading
        'WHERE' or is an empty string.
        """
        params: List[str] = []
        clauses: List[str] = []

        if host:
            clauses.append("host LIKE ?")
            params.append(f"%{host}%")

        if self.only_zybooks:
            clauses.append("host LIKE ?")
            params.append("%zybooks%")

        if clauses:
            return "WHERE " + " AND ".join(clauses), params
        return "", params
    
    def export_har(self, output_file: str, limit: int = 100):
        """Export traffic as HAR file"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        clause, params = self._host_clause_and_params(None)
        params_with_limit = params + [limit]
        cursor.execute(f"SELECT * FROM requests {clause} ORDER BY timestamp DESC LIMIT ?", tuple(params_with_limit))
        rows = cursor.fetchall()
        conn.close()
        
        # Build HAR format
        har = {
            "log": {
                "version": "1.2",
                "creator": {"name": "Traffic Analyzer", "version": "2.0"},
                "entries": []
            }
        }
        
        for row in rows:
            entry = {
                "startedDateTime": datetime.fromtimestamp(row['timestamp']).isoformat(),
                "time": row['duration'] * 1000,
                "request": {
                    "method": row['method'],
                    "url": row['url'],
                    "httpVersion": "HTTP/1.1",
                    "headers": [{"name": k, "value": v} for k, v in json.loads(row['headers']).items()],
                    "queryString": [],
                    "bodySize": len(row['body']) if row['body'] else 0
                },
                "response": {
                    "status": row['response_status'],
                    "statusText": "OK",
                    "httpVersion": "HTTP/1.1",
                    "headers": [{"name": k, "value": v} for k, v in json.loads(row['response_headers']).items()],
                    "content": {
                        "size": len(row['response_body']) if row['response_body'] else 0,
                        "mimeType": "application/octet-stream"
                    },
                    "bodySize": len(row['response_body']) if row['response_body'] else 0
                }
            }
            har["log"]["entries"].append(entry)
        
        with open(output_file, 'w') as f:
            json.dump(har, f, indent=2)
        
        print(f"✅ Exported {len(rows)} requests to {output_file}")
    
    def clear_database(self):
        """Clear all captured traffic"""
        response = input("⚠️  Are you sure you want to clear all traffic? (yes/no): ")
        if response.lower() == 'yes':
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM requests")
            conn.commit()
            conn.close()
            print("✅ Database cleared")
        else:
            print("❌ Cancelled")


async def run_proxy(port: int = 8080):
    """Run the mitmproxy server"""
    opts = options.Options(listen_host='0.0.0.0', listen_port=port)
    
    master = dump.DumpMaster(
        opts,
        with_termlog=False,
        with_dumper=False,
    )
    
    master.addons.add(TrafficCapture())
    
    try:
        print(f"🚀 Proxy server starting on port {port}...")
        print(f"📊 Configure your browser to use: localhost:{port}")
        print(f"📜 Certificate: ./certs/mitmproxy-ca-cert.pem")
        print(f"💾 Database: traffic.db")
        print(f"━" * 80)
        await master.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down proxy...")
        master.shutdown()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="HTTP Traffic Analyzer - Burp Suite Style with Copilot Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s proxy                    # Start proxy server
  %(prog)s stats                    # Show traffic statistics
  %(prog)s list                     # List recent requests
  %(prog)s list --host zybooks      # Filter by host
  %(prog)s show 42                  # Show request details
  %(prog)s analyze                  # Analyze recent traffic with Copilot
  %(prog)s analyze --id 42          # Analyze specific request
  %(prog)s search "api_key"         # Search traffic
  %(prog)s export traffic.har       # Export to HAR format
  %(prog)s clear                    # Clear database
        """
    )
    
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--port', type=int, default=8080, help='Proxy port (default: 8080)')
    parser.add_argument('--host', help='Filter by host')
    parser.add_argument('--limit', type=int, default=10, help='Limit results')
    parser.add_argument('--id', type=int, help='Request ID')
    parser.add_argument('--zybooks', action='store_true', help='Only include requests from zybooks hosts')
    
    args = parser.parse_args()
    
    cli = TrafficAnalyzerCLI()
    # Apply global filters from args
    if args.zybooks:
        cli.only_zybooks = True
    
    try:
        if args.command == 'proxy':
            asyncio.run(run_proxy(args.port))
        
        elif args.command == 'stats':
            cli.get_stats()
        
        elif args.command == 'list':
            cli.list_requests(limit=args.limit, host=args.host)
        
        elif args.command == 'show':
            if not args.args:
                print("❌ Error: Request ID required")
                sys.exit(1)
            cli.show_request(int(args.args[0]))
        
        elif args.command == 'analyze':
            cli.analyze_with_copilot(request_id=args.id)
        
        elif args.command == 'search':
            if not args.args:
                print("❌ Error: Search query required")
                sys.exit(1)
            cli.search(args.args[0])
        
        elif args.command == 'export':
            if not args.args:
                print("❌ Error: Output file required")
                sys.exit(1)
            cli.export_har(args.args[0], limit=args.limit)
        
        elif args.command == 'clear':
            cli.clear_database()
        
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
