#!/usr/bin/env python3
"""
Quick Test Script for Traffic Analyzer
Tests the basic functionality without needing to configure a browser
"""

import asyncio
import aiohttp
import time

async def test_proxy():
    """Test the proxy by making some HTTP requests through it"""
    
    proxy = "http://localhost:8080"
    
    print("🧪 Testing Traffic Analyzer Proxy\n")
    print("="*60)
    
    # Wait for proxy to start
    print("⏳ Waiting for proxy to start...")
    await asyncio.sleep(3)
    
    test_urls = [
        "http://httpbin.org/get",
        "http://httpbin.org/post",
        "http://httpbin.org/headers",
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in test_urls:
            try:
                print(f"\n📡 Testing: {url}")
                start = time.time()
                
                async with session.get(url, proxy=proxy, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    duration = time.time() - start
                    print(f"   ✅ Status: {response.status}")
                    print(f"   ⏱️  Duration: {duration*1000:.0f}ms")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("✅ Test complete!")
    print("📊 Check the web interface at http://localhost:8081")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_proxy())
