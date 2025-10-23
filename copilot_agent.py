#!/usr/bin/env python3
"""
Copilot Agent Integration for Traffic Analysis
This module provides AI-powered analysis of captured traffic
"""

import json
import sqlite3
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RequestAnalysis:
    """Analysis results for a HTTP request"""
    request_id: int
    security_score: float
    vulnerabilities: List[str]
    recommendations: List[str]
    summary: str
    insights: Dict[str, any]


class CopilotAgent:
    """AI Agent for analyzing HTTP traffic"""
    
    def __init__(self, db_path: str = "traffic.db"):
        self.db_path = db_path
    
    def analyze_request(self, request_id: int) -> RequestAnalysis:
        """
        Analyze a single request for security issues, performance, and best practices
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise ValueError(f"Request {request_id} not found")
        
        req = dict(row)
        
        # Analyze various aspects
        vulnerabilities = []
        recommendations = []
        security_score = 100.0
        
        # Parse headers
        headers = json.loads(req['headers'])
        response_headers = json.loads(req['response_headers'])
        
        # Security analysis
        security_issues = self._check_security(req, headers, response_headers)
        vulnerabilities.extend(security_issues)
        security_score -= len(security_issues) * 10
        
        # Performance analysis
        perf_issues = self._check_performance(req)
        recommendations.extend(perf_issues)
        
        # Best practices
        best_practices = self._check_best_practices(req, headers, response_headers)
        recommendations.extend(best_practices)
        
        # Generate summary
        summary = self._generate_summary(req, vulnerabilities, recommendations)
        
        # Additional insights
        insights = {
            "method": req['method'],
            "status_code": req['response_status'],
            "duration_ms": req['duration'] * 1000,
            "has_auth": any('auth' in h.lower() for h in headers.keys()),
            "content_type": headers.get('content-type', 'unknown'),
            "size_bytes": len(req.get('body', '') or '')
        }
        
        return RequestAnalysis(
            request_id=request_id,
            security_score=max(0, security_score),
            vulnerabilities=vulnerabilities,
            recommendations=recommendations,
            summary=summary,
            insights=insights
        )
    
    def _check_security(self, req: Dict, headers: Dict, response_headers: Dict) -> List[str]:
        """Check for security vulnerabilities"""
        issues = []
        
        # Check for sensitive data in URL
        url_lower = req['url'].lower()
        sensitive_keywords = ['password', 'token', 'secret', 'api_key', 'apikey']
        if any(keyword in url_lower for keyword in sensitive_keywords):
            issues.append("⚠️ Sensitive data detected in URL (should use POST body instead)")
        
        # Check for missing security headers
        if not response_headers.get('strict-transport-security'):
            issues.append("Missing HSTS header (Strict-Transport-Security)")
        
        if not response_headers.get('x-content-type-options'):
            issues.append("Missing X-Content-Type-Options header")
        
        if not response_headers.get('x-frame-options'):
            issues.append("Missing X-Frame-Options header (clickjacking protection)")
        
        # Check protocol
        if req['protocol'] == 'http':
            issues.append("🔓 Insecure HTTP protocol (should use HTTPS)")
        
        # Check for exposed authorization
        if 'authorization' in [h.lower() for h in headers.keys()]:
            auth_value = headers.get('Authorization', headers.get('authorization', ''))
            if auth_value.startswith('Basic '):
                issues.append("⚠️ Basic authentication detected (consider using OAuth or JWT)")
        
        # Check for SQL injection patterns in request
        body = req.get('body', '')
        sql_patterns = ['SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'DROP ', 'UNION ']
        if any(pattern in body.upper() for pattern in sql_patterns):
            issues.append("🚨 Potential SQL injection attempt detected")
        
        # Check for XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
        if any(pattern in body.lower() for pattern in xss_patterns):
            issues.append("🚨 Potential XSS payload detected")
        
        return issues
    
    def _check_performance(self, req: Dict) -> List[str]:
        """Check for performance issues"""
        recommendations = []
        
        duration = req['duration']
        
        if duration > 5:
            recommendations.append(f"⏱️ Very slow request ({duration:.2f}s) - investigate server performance")
        elif duration > 2:
            recommendations.append(f"⏱️ Slow request ({duration:.2f}s) - consider optimization")
        
        # Check response size
        response_body = req.get('response_body', '')
        if len(response_body) > 1000000:  # 1MB
            recommendations.append(f"📦 Large response size ({len(response_body)} bytes) - consider pagination or compression")
        
        return recommendations
    
    def _check_best_practices(self, req: Dict, headers: Dict, response_headers: Dict) -> List[str]:
        """Check for best practices"""
        recommendations = []
        
        # Check for caching headers
        if req['method'] == 'GET':
            if not response_headers.get('cache-control') and not response_headers.get('etag'):
                recommendations.append("💡 Consider adding cache headers for GET requests")
        
        # Check for compression
        if 'content-encoding' not in [h.lower() for h in response_headers.keys()]:
            recommendations.append("💡 Response is not compressed - enable gzip/brotli compression")
        
        # Check for API versioning
        if '/api/' in req['path'] and not any(v in req['path'] for v in ['/v1/', '/v2/', '/v3/']):
            recommendations.append("💡 API endpoint should include version number")
        
        # Check for CORS headers
        if response_headers.get('access-control-allow-origin') == '*':
            recommendations.append("⚠️ CORS allows all origins - consider restricting to specific domains")
        
        return recommendations
    
    def _generate_summary(self, req: Dict, vulnerabilities: List[str], recommendations: List[str]) -> str:
        """Generate a human-readable summary"""
        status = req['response_status']
        method = req['method']
        url = req['url']
        duration = req['duration']
        
        summary = f"{method} request to {url} "
        
        if status:
            if 200 <= status < 300:
                summary += f"✅ succeeded ({status}) "
            elif 300 <= status < 400:
                summary += f"↪️ redirected ({status}) "
            elif 400 <= status < 500:
                summary += f"⚠️ client error ({status}) "
            else:
                summary += f"❌ server error ({status}) "
        
        summary += f"in {duration*1000:.0f}ms. "
        
        if vulnerabilities:
            summary += f"Found {len(vulnerabilities)} security issues. "
        else:
            summary += "No security issues detected. "
        
        if recommendations:
            summary += f"{len(recommendations)} optimization suggestions available."
        
        return summary
    
    def analyze_session(self, limit: int = 100) -> Dict:
        """Analyze recent traffic patterns"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM requests 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"message": "No traffic to analyze"}
        
        # Analyze patterns
        total_requests = len(rows)
        methods = {}
        status_codes = {}
        hosts = {}
        total_duration = 0
        security_issues = 0
        
        for row in rows:
            req = dict(row)
            
            # Count methods
            methods[req['method']] = methods.get(req['method'], 0) + 1
            
            # Count status codes
            status = req['response_status']
            if status:
                status_codes[status] = status_codes.get(status, 0) + 1
            
            # Count hosts
            hosts[req['host']] = hosts.get(req['host'], 0) + 1
            
            # Sum duration
            total_duration += req['duration']
            
            # Quick security check
            if req['protocol'] == 'http':
                security_issues += 1
        
        avg_duration = total_duration / total_requests if total_requests > 0 else 0
        
        return {
            "session_summary": {
                "total_requests": total_requests,
                "avg_response_time_ms": avg_duration * 1000,
                "unique_hosts": len(hosts),
                "security_issues_found": security_issues
            },
            "methods": methods,
            "status_codes": status_codes,
            "top_hosts": sorted(hosts.items(), key=lambda x: x[1], reverse=True)[:10],
            "recommendations": self._generate_session_recommendations(rows)
        }
    
    def _generate_session_recommendations(self, rows: List) -> List[str]:
        """Generate recommendations for the entire session"""
        recommendations = []
        
        # Check for insecure connections
        http_count = sum(1 for r in rows if dict(r)['protocol'] == 'http')
        if http_count > 0:
            recommendations.append(f"🔓 {http_count} requests using insecure HTTP - migrate to HTTPS")
        
        # Check for failed requests
        failed_count = sum(1 for r in rows if dict(r)['response_status'] and dict(r)['response_status'] >= 400)
        if failed_count > len(rows) * 0.1:  # More than 10% failures
            recommendations.append(f"⚠️ High failure rate ({failed_count}/{len(rows)}) - investigate errors")
        
        # Check for slow requests
        slow_count = sum(1 for r in rows if dict(r)['duration'] > 2)
        if slow_count > 0:
            recommendations.append(f"⏱️ {slow_count} slow requests detected - optimize performance")
        
        return recommendations


def main():
    """Test the Copilot Agent"""
    agent = CopilotAgent()
    
    # Analyze recent session
    print("📊 Analyzing recent traffic session...\n")
    session_analysis = agent.analyze_session()
    print(json.dumps(session_analysis, indent=2))
    
    # Analyze specific request (if any exist)
    conn = sqlite3.connect("traffic.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM requests ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        request_id = row[0]
        print(f"\n🔍 Analyzing request #{request_id}...\n")
        analysis = agent.analyze_request(request_id)
        print(f"Summary: {analysis.summary}")
        print(f"Security Score: {analysis.security_score}/100")
        
        if analysis.vulnerabilities:
            print("\n⚠️ Vulnerabilities:")
            for vuln in analysis.vulnerabilities:
                print(f"  - {vuln}")
        
        if analysis.recommendations:
            print("\n💡 Recommendations:")
            for rec in analysis.recommendations:
                print(f"  - {rec}")
        
        print(f"\n📈 Insights:")
        print(json.dumps(analysis.insights, indent=2))


if __name__ == "__main__":
    main()
