#!/usr/bin/env python3
"""
Test admin panel endpoints
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
    """Test admin panel endpoints"""
    base_url = "http://localhost:8002"
    
    endpoints = [
        "/stats",
        "/model-info", 
        "/claims-analysis"
    ]
    
    print("🧪 Testing Admin Panel Endpoints")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n🔍 Testing: {url}")
        
        result = test_endpoint(url)
        
        if "error" in result:
            print(f"❌ Failed: {result['error']}")
        else:
            print(f"✅ Success: Endpoint working")
            # Print key fields for verification
            if endpoint == "/stats":
                print(f"   Total Policies: {result.get('total_policies', 'N/A')}")
                print(f"   Avg Claim: ₹{result.get('avg_claim', 0):.2f}")
            elif endpoint == "/model-info":
                print(f"   Status: {result.get('status', 'N/A')}")
                print(f"   Model Type: {result.get('model_type', 'N/A')}")
            elif endpoint == "/claims-analysis":
                print(f"   Age Groups: {len(result.get('age_groups', {}))}")
                print(f"   Regions: {len(result.get('region_analysis', {}))}")

if __name__ == "__main__":
    main()
