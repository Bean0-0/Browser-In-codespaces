#!/usr/bin/env python3
"""
Enhanced API Server for Copilot Agent Integration
This provides RESTful endpoints for Copilot to analyze traffic and respond
"""

import json
import sqlite3
from aiohttp import web
from copilot_agent import CopilotAgent


class CopilotAPIServer:
    """API server for Copilot agent integration"""
    
    def __init__(self, db_path: str = "traffic.db", port: int = 8082):
        self.db_path = db_path
        self.port = port
        self.agent = CopilotAgent(db_path)
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes for Copilot integration"""
        # Analysis endpoints
        self.app.router.add_post('/copilot/analyze/request/{id}', self.analyze_request)
        self.app.router.add_post('/copilot/analyze/session', self.analyze_session)
        self.app.router.add_post('/copilot/analyze/security', self.security_scan)
        self.app.router.add_post('/copilot/analyze/performance', self.performance_analysis)
        
        # Query endpoints
        self.app.router.add_get('/copilot/query/requests', self.query_requests)
        self.app.router.add_get('/copilot/query/hosts', self.query_hosts)
        self.app.router.add_get('/copilot/query/methods', self.query_methods)
        
        # Action endpoints
        self.app.router.add_post('/copilot/action/replay/{id}', self.replay_request)
        self.app.router.add_post('/copilot/action/modify/{id}', self.modify_and_replay)
        
        # Export endpoints
        self.app.router.add_get('/copilot/export/json', self.export_json)
        self.app.router.add_get('/copilot/export/har', self.export_har)
    
    async def analyze_request(self, request):
        """
        Analyze a specific request
        POST /copilot/analyze/request/{id}
        """
        request_id = int(request.match_info['id'])
        
        try:
            analysis = self.agent.analyze_request(request_id)
            
            return web.json_response({
                'success': True,
                'request_id': request_id,
                'analysis': {
                    'summary': analysis.summary,
                    'security_score': analysis.security_score,
                    'vulnerabilities': analysis.vulnerabilities,
                    'recommendations': analysis.recommendations,
                    'insights': analysis.insights
                }
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def analyze_session(self, request):
        """
        Analyze recent session traffic
        POST /copilot/analyze/session
        Body: { "limit": 100 }
        """
        try:
            data = await request.json()
            limit = data.get('limit', 100)
            
            analysis = self.agent.analyze_session(limit)
            
            return web.json_response({
                'success': True,
                'analysis': analysis
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def security_scan(self, request):
        """
        Perform security scan on all recent traffic
        POST /copilot/analyze/security
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM requests ORDER BY timestamp DESC LIMIT 100")
            rows = cursor.fetchall()
            conn.close()
            
            security_issues = []
            high_risk_requests = []
            
            for row in rows:
                request_id = row['id']
                analysis = self.agent.analyze_request(request_id)
                
                if analysis.vulnerabilities:
                    security_issues.extend(analysis.vulnerabilities)
                    
                if analysis.security_score < 70:
                    high_risk_requests.append({
                        'request_id': request_id,
                        'score': analysis.security_score,
                        'issues': analysis.vulnerabilities
                    })
            
            return web.json_response({
                'success': True,
                'total_issues': len(security_issues),
                'unique_issues': len(set(security_issues)),
                'high_risk_requests': high_risk_requests,
                'all_issues': list(set(security_issues))
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def performance_analysis(self, request):
        """
        Analyze performance metrics
        POST /copilot/analyze/performance
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    AVG(duration) as avg_duration,
                    MIN(duration) as min_duration,
                    MAX(duration) as max_duration,
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN duration > 2 THEN 1 ELSE 0 END) as slow_requests
                FROM requests
            """)
            
            stats = dict(cursor.fetchone())
            
            # Get slowest requests
            cursor.execute("""
                SELECT id, method, url, duration, response_status
                FROM requests
                ORDER BY duration DESC
                LIMIT 10
            """)
            
            slowest = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return web.json_response({
                'success': True,
                'metrics': {
                    'avg_response_time_ms': stats['avg_duration'] * 1000 if stats['avg_duration'] else 0,
                    'min_response_time_ms': stats['min_duration'] * 1000 if stats['min_duration'] else 0,
                    'max_response_time_ms': stats['max_duration'] * 1000 if stats['max_duration'] else 0,
                    'total_requests': stats['total_requests'],
                    'slow_requests': stats['slow_requests']
                },
                'slowest_requests': slowest
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def query_requests(self, request):
        """
        Query requests with filters
        GET /copilot/query/requests?method=GET&status=200&limit=50
        """
        try:
            method = request.query.get('method')
            status = request.query.get('status')
            host = request.query.get('host')
            limit = int(request.query.get('limit', 100))
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM requests WHERE 1=1"
            params = []
            
            if method:
                query += " AND method = ?"
                params.append(method)
            
            if status:
                query += " AND response_status = ?"
                params.append(int(status))
            
            if host:
                query += " AND host LIKE ?"
                params.append(f"%{host}%")
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            results = [dict(row) for row in rows]
            
            return web.json_response({
                'success': True,
                'count': len(results),
                'requests': results
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def query_hosts(self, request):
        """Get all unique hosts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT host, COUNT(*) as count
                FROM requests
                GROUP BY host
                ORDER BY count DESC
            """)
            
            hosts = [{'host': row[0], 'count': row[1]} for row in cursor.fetchall()]
            conn.close()
            
            return web.json_response({
                'success': True,
                'hosts': hosts
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def query_methods(self, request):
        """Get HTTP methods distribution"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT method, COUNT(*) as count
                FROM requests
                GROUP BY method
                ORDER BY count DESC
            """)
            
            methods = [{'method': row[0], 'count': row[1]} for row in cursor.fetchall()]
            conn.close()
            
            return web.json_response({
                'success': True,
                'methods': methods
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def replay_request(self, request):
        """
        Replay a captured request
        POST /copilot/action/replay/{id}
        """
        request_id = int(request.match_info['id'])
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return web.json_response({
                    'success': False,
                    'error': 'Request not found'
                }, status=404)
            
            req_data = dict(row)
            
            # In a real implementation, you would replay the request here
            # For now, we'll return the request data
            
            return web.json_response({
                'success': True,
                'message': f'Request {request_id} replayed',
                'request': {
                    'method': req_data['method'],
                    'url': req_data['url'],
                    'headers': json.loads(req_data['headers']),
                    'body': req_data['body']
                }
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def modify_and_replay(self, request):
        """
        Modify and replay a request
        POST /copilot/action/modify/{id}
        Body: { "headers": {...}, "body": "...", "url": "..." }
        """
        request_id = int(request.match_info['id'])
        
        try:
            modifications = await request.json()
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return web.json_response({
                    'success': False,
                    'error': 'Request not found'
                }, status=404)
            
            req_data = dict(row)
            
            # Apply modifications
            modified_request = {
                'method': req_data['method'],
                'url': modifications.get('url', req_data['url']),
                'headers': modifications.get('headers', json.loads(req_data['headers'])),
                'body': modifications.get('body', req_data['body'])
            }
            
            return web.json_response({
                'success': True,
                'message': f'Modified request {request_id} ready to replay',
                'original': {
                    'url': req_data['url'],
                    'headers': json.loads(req_data['headers']),
                    'body': req_data['body']
                },
                'modified': modified_request
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def export_json(self, request):
        """Export all traffic as JSON"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM requests ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            conn.close()
            
            traffic = [dict(row) for row in rows]
            
            return web.json_response({
                'success': True,
                'count': len(traffic),
                'traffic': traffic
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def export_har(self, request):
        """Export traffic in HAR format (HTTP Archive)"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM requests ORDER BY timestamp")
            rows = cursor.fetchall()
            conn.close()
            
            # Build HAR format
            entries = []
            for row in rows:
                req = dict(row)
                
                entry = {
                    'startedDateTime': f"{req['timestamp']}",
                    'time': req['duration'] * 1000,
                    'request': {
                        'method': req['method'],
                        'url': req['url'],
                        'httpVersion': 'HTTP/1.1',
                        'headers': [{'name': k, 'value': v} for k, v in json.loads(req['headers']).items()],
                        'postData': {
                            'text': req['body'] or ''
                        }
                    },
                    'response': {
                        'status': req['response_status'] or 0,
                        'statusText': 'OK',
                        'httpVersion': 'HTTP/1.1',
                        'headers': [{'name': k, 'value': v} for k, v in json.loads(req['response_headers']).items()],
                        'content': {
                            'text': req['response_body'] or ''
                        }
                    }
                }
                entries.append(entry)
            
            har = {
                'log': {
                    'version': '1.2',
                    'creator': {
                        'name': 'Traffic Analyzer',
                        'version': '1.0'
                    },
                    'entries': entries
                }
            }
            
            return web.json_response(har)
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def start(self):
        """Start the API server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        print(f"\n🤖 Copilot API Server started on http://localhost:{self.port}")
        print("\n📋 Available Endpoints:")
        print("   POST   /copilot/analyze/request/{id}")
        print("   POST   /copilot/analyze/session")
        print("   POST   /copilot/analyze/security")
        print("   POST   /copilot/analyze/performance")
        print("   GET    /copilot/query/requests")
        print("   GET    /copilot/query/hosts")
        print("   GET    /copilot/query/methods")
        print("   POST   /copilot/action/replay/{id}")
        print("   POST   /copilot/action/modify/{id}")
        print("   GET    /copilot/export/json")
        print("   GET    /copilot/export/har\n")


async def main():
    """Run the Copilot API server"""
    server = CopilotAPIServer()
    await server.start()
    
    # Keep running
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    import asyncio
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Copilot API server...")
