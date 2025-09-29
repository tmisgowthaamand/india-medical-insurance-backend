#!/usr/bin/env python3
"""
Test model status endpoints
"""

import urllib.request
import urllib.error
import json

def test_endpoint(url, name):
    """Test an endpoint"""
    try:
        print(f"🔍 Testing: {name} - {url}")
        
        with urllib.request.urlopen(url) as response:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            print(f"✅ Success: {result}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            print(f"   Error details: {error_data}")
        except:
            print(f"   Raw error: {error_body}")
        return False
        
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def main():
    """Test model endpoints"""
    base_url = "http://localhost:8002"
    
    endpoints = [
        ("/model-status", "Public Model Status"),
        ("/model-info", "Protected Model Info (should fail)"),
    ]
    
    print("🧪 Testing Model Endpoints")
    print("=" * 50)
    
    for endpoint, name in endpoints:
        url = base_url + endpoint
        test_endpoint(url, name)
        print()

if __name__ == "__main__":
    main()
