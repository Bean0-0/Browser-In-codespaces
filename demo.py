#!/usr/bin/env python3
"""
Complete Demo: Traffic Analyzer with Copilot Integration
This script demonstrates the full workflow
"""

import asyncio
import aiohttp
import requests
import time
import json
from datetime import datetime


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


async def generate_sample_traffic():
    """Generate sample traffic through the proxy"""
    print_section("🌐 Generating Sample Traffic")
    
    proxy = "http://localhost:8080"
    
    # Sample URLs to test
    test_scenarios = [
        {
            "name": "API Call (Secure)",
            "url": "https://api.github.com/users/octocat",
            "method": "GET"
        },
        {
            "name": "API Call (Insecure)",
            "url": "http://httpbin.org/get",
            "method": "GET"
        },
        {
            "name": "POST Request",
            "url": "http://httpbin.org/post",
            "method": "POST",
            "data": {"user": "test", "password": "secret123"}
        },
        {
            "name": "Headers Test",
            "url": "http://httpbin.org/headers",
            "method": "GET"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for scenario in test_scenarios:
            try:
                print(f"📡 {scenario['name']}: {scenario['url']}")
                
                if scenario['method'] == 'GET':
                    async with session.get(
                        scenario['url'], 
                        proxy=proxy,
                        timeout=aiohttp.ClientTimeout(total=10),
                        ssl=False
                    ) as resp:
                        print(f"   ✅ Status: {resp.status}")
                else:
                    async with session.post(
                        scenario['url'],
                        json=scenario['data'],
                        proxy=proxy,
                        timeout=aiohttp.ClientTimeout(total=10),
                        ssl=False
                    ) as resp:
                        print(f"   ✅ Status: {resp.status}")
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ⚠️ Error: {str(e)}")
    
    print("\n✅ Sample traffic generated!")
    print("⏳ Waiting for traffic to be captured...")
    await asyncio.sleep(2)


def analyze_with_copilot():
    """Demonstrate Copilot analysis capabilities"""
    
    print_section("🤖 Copilot Analysis")
    
    base_url = "http://localhost:8082"
    
    try:
        # 1. Security Scan
        print("🔒 Running Security Scan...")
        response = requests.post(f"{base_url}/copilot/analyze/security", timeout=5)
        
        if response.status_code == 200:
            security = response.json()
            print(f"\n📊 Security Scan Results:")
            print(f"   Total Issues: {security.get('total_issues', 0)}")
            print(f"   Unique Issues: {security.get('unique_issues', 0)}")
            print(f"   High Risk Requests: {len(security.get('high_risk_requests', []))}")
            
            if security.get('all_issues'):
                print(f"\n⚠️ Issues Found:")
                for issue in security['all_issues'][:5]:
                    print(f"   - {issue}")
        
        time.sleep(1)
        
        # 2. Performance Analysis
        print("\n\n⚡ Analyzing Performance...")
        response = requests.post(f"{base_url}/copilot/analyze/performance", timeout=5)
        
        if response.status_code == 200:
            perf = response.json()
            metrics = perf.get('metrics', {})
            
            print(f"\n📈 Performance Metrics:")
            print(f"   Average Response Time: {metrics.get('avg_response_time_ms', 0):.2f}ms")
            print(f"   Min Response Time: {metrics.get('min_response_time_ms', 0):.2f}ms")
            print(f"   Max Response Time: {metrics.get('max_response_time_ms', 0):.2f}ms")
            print(f"   Total Requests: {metrics.get('total_requests', 0)}")
            print(f"   Slow Requests (>2s): {metrics.get('slow_requests', 0)}")
            
            if perf.get('slowest_requests'):
                print(f"\n🐌 Slowest Requests:")
                for req in perf['slowest_requests'][:3]:
                    print(f"   - {req['method']} {req['url']}: {req['duration']*1000:.0f}ms")
        
        time.sleep(1)
        
        # 3. Session Analysis
        print("\n\n📊 Analyzing Session...")
        response = requests.post(
            f"{base_url}/copilot/analyze/session",
            json={"limit": 50},
            timeout=5
        )
        
        if response.status_code == 200:
            session_data = response.json()
            analysis = session_data.get('analysis', {})
            summary = analysis.get('session_summary', {})
            
            print(f"\n📋 Session Summary:")
            print(f"   Total Requests: {summary.get('total_requests', 0)}")
            print(f"   Avg Response Time: {summary.get('avg_response_time_ms', 0):.2f}ms")
            print(f"   Unique Hosts: {summary.get('unique_hosts', 0)}")
            print(f"   Security Issues: {summary.get('security_issues_found', 0)}")
            
            if analysis.get('top_hosts'):
                print(f"\n🌐 Top Hosts:")
                for host, count in analysis['top_hosts'][:5]:
                    print(f"   - {host}: {count} requests")
            
            if analysis.get('methods'):
                print(f"\n🔧 HTTP Methods:")
                for method, count in analysis['methods'].items():
                    print(f"   - {method}: {count}")
        
        time.sleep(1)
        
        # 4. Query Requests
        print("\n\n🔍 Querying Requests...")
        response = requests.get(
            f"{base_url}/copilot/query/requests",
            params={"limit": 5},
            timeout=5
        )
        
        if response.status_code == 200:
            query_result = response.json()
            requests_list = query_result.get('requests', [])
            
            print(f"\n📝 Recent Requests ({len(requests_list)}):")
            for req in requests_list[:5]:
                status_emoji = "✅" if 200 <= req['response_status'] < 300 else "❌"
                print(f"   {status_emoji} {req['method']} {req['url']} - {req['response_status']}")
        
        # 5. Detailed Request Analysis
        if requests_list:
            print("\n\n🔬 Detailed Request Analysis...")
            request_id = requests_list[0]['id']
            
            response = requests.post(
                f"{base_url}/copilot/analyze/request/{request_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                detail = response.json()
                analysis = detail.get('analysis', {})
                
                print(f"\n📄 Request #{request_id} Analysis:")
                print(f"   Summary: {analysis.get('summary', 'N/A')}")
                print(f"   Security Score: {analysis.get('security_score', 0)}/100")
                
                if analysis.get('vulnerabilities'):
                    print(f"\n   ⚠️ Vulnerabilities:")
                    for vuln in analysis['vulnerabilities']:
                        print(f"      - {vuln}")
                
                if analysis.get('recommendations'):
                    print(f"\n   💡 Recommendations:")
                    for rec in analysis['recommendations'][:3]:
                        print(f"      - {rec}")
                
                insights = analysis.get('insights', {})
                print(f"\n   📊 Insights:")
                print(f"      Method: {insights.get('method', 'N/A')}")
                print(f"      Status: {insights.get('status_code', 'N/A')}")
                print(f"      Duration: {insights.get('duration_ms', 0):.2f}ms")
                print(f"      Has Auth: {insights.get('has_auth', False)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Copilot API server!")
        print("   Make sure to run: python3 copilot_api.py")
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")


def demonstrate_actions():
    """Demonstrate request replay and modification"""
    
    print_section("🎬 Demonstrating Actions")
    
    base_url = "http://localhost:8082"
    
    try:
        # Get a request to work with
        response = requests.get(
            f"{base_url}/copilot/query/requests",
            params={"limit": 1},
            timeout=5
        )
        
        if response.status_code == 200:
            requests_list = response.json().get('requests', [])
            
            if requests_list:
                request_id = requests_list[0]['id']
                
                # 1. Replay Request
                print(f"▶️ Replaying Request #{request_id}...")
                response = requests.post(
                    f"{base_url}/copilot/action/replay/{request_id}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {result.get('message', 'Success')}")
                
                time.sleep(1)
                
                # 2. Modify and Replay
                print(f"\n✏️ Modifying Request #{request_id}...")
                response = requests.post(
                    f"{base_url}/copilot/action/modify/{request_id}",
                    json={
                        "headers": {
                            "X-Custom-Header": "Modified-By-Copilot",
                            "User-Agent": "Traffic-Analyzer-Demo/1.0"
                        }
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {result.get('message', 'Success')}")
                    
                    if result.get('modified'):
                        modified = result['modified']
                        print(f"\n   Modified Request:")
                        print(f"      URL: {modified.get('url', 'N/A')}")
                        print(f"      Headers: {len(modified.get('headers', {}))} headers")
            else:
                print("   ℹ️ No requests available to demonstrate actions")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Copilot API server!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def export_data():
    """Demonstrate data export"""
    
    print_section("💾 Exporting Data")
    
    base_url = "http://localhost:8082"
    
    try:
        # Export as JSON
        print("📄 Exporting as JSON...")
        response = requests.get(f"{base_url}/copilot/export/json", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            filename = f"traffic_export_{int(time.time())}.json"
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"   ✅ Exported to {filename}")
            print(f"   📊 {data.get('count', 0)} requests exported")
        
        time.sleep(1)
        
        # Export as HAR
        print("\n🗃️ Exporting as HAR (HTTP Archive)...")
        response = requests.get(f"{base_url}/copilot/export/har", timeout=5)
        
        if response.status_code == 200:
            har_data = response.json()
            filename = f"traffic_export_{int(time.time())}.har"
            
            with open(filename, 'w') as f:
                json.dump(har_data, f, indent=2)
            
            entries = len(har_data.get('log', {}).get('entries', []))
            print(f"   ✅ Exported to {filename}")
            print(f"   📊 {entries} entries exported")
            print(f"   💡 Can be imported into browser dev tools or other tools")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Copilot API server!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def main():
    """Run the complete demo"""
    
    print("\n" + "🚀"*35)
    print("   TRAFFIC ANALYZER - COMPLETE DEMO")
    print("   Burp Suite Style Tool with Copilot Integration")
    print("🚀"*35)
    
    print("\n📋 Prerequisites:")
    print("   1. Proxy Server running (python3 proxy_server.py)")
    print("   2. Copilot API Server running (python3 copilot_api.py)")
    print("\n⏳ Starting demo in 3 seconds...")
    await asyncio.sleep(3)
    
    # Generate traffic
    try:
        await generate_sample_traffic()
    except Exception as e:
        print(f"⚠️ Could not generate traffic: {str(e)}")
        print("   Make sure proxy server is running on port 8080")
    
    # Analyze with Copilot
    analyze_with_copilot()
    
    # Demonstrate actions
    demonstrate_actions()
    
    # Export data
    export_data()
    
    # Final summary
    print_section("🎉 Demo Complete!")
    
    print("What you learned:")
    print("  ✅ How to capture browser traffic")
    print("  ✅ How Copilot analyzes security issues")
    print("  ✅ How to get performance insights")
    print("  ✅ How to replay and modify requests")
    print("  ✅ How to export data for further analysis")
    
    print("\n📚 Next Steps:")
    print("  1. Check the web interface at http://localhost:8081")
    print("  2. Review COPILOT_GUIDE.md for more examples")
    print("  3. Try the API endpoints manually")
    print("  4. Build your own automation scripts")
    
    print("\n💡 Tip: Use Copilot Chat to ask questions about the captured traffic!")
    print("   Example: 'Show me all failed requests'")
    print("   Example: 'What security issues did you find?'\n")


if __name__ == "__main__":
    asyncio.run(main())
