#!/usr/bin/env python3
"""
Test stats endpoint specifically
"""

import urllib.request
import urllib.error
import json

def test_stats():
    """Test stats endpoint with detailed error info"""
    url = "http://localhost:8002/stats"
    
    try:
        print(f"🔍 Testing: {url}")
        
        with urllib.request.urlopen(url) as response:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            print("✅ Success!")
            print(f"   Total Policies: {result.get('total_policies', 'N/A')}")
            print(f"   Avg Claim: ₹{result.get('avg_claim', 0):.2f}")
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

if __name__ == "__main__":
    test_stats()
