#!/usr/bin/env python3
"""
Test backend endpoints
"""

import urllib.request
import json

def test_endpoint(url):
    """Test an endpoint"""
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def main():
    """Test backend endpoints"""
    base_url = "http://localhost:8002"
    
    endpoints = [
        "/health",
        "/",
        "/cors-test"
    ]
    
    print("🧪 Testing Backend Endpoints")
    print("=" * 40)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n🔍 Testing: {url}")
        
        result = test_endpoint(url)
        
        if "error" in result:
            print(f"❌ Failed: {result['error']}")
        else:
            print(f"✅ Success: {result}")

if __name__ == "__main__":
    main()
