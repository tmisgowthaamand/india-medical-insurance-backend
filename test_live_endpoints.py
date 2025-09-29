#!/usr/bin/env python3
"""
Test live endpoints that include user predictions
"""

import urllib.request
import urllib.error
import json

def test_endpoint(url, name):
    """Test an endpoint"""
    try:
        print(f"🔍 Testing: {name}")
        print(f"   URL: {url}")
        
        with urllib.request.urlopen(url) as response:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            
            print(f"✅ Success!")
            
            # Show key metrics for different endpoints
            if 'total_policies' in result:
                print(f"   Total Policies: {result.get('total_policies', 'N/A')}")
                print(f"   Avg Claim: ₹{result.get('avg_claim', 0):.2f}")
                print(f"   Avg Premium: ₹{result.get('avg_premium', 0):.2f}")
            elif 'age_groups' in result:
                print(f"   Age Groups: {len(result.get('age_groups', {}))}")
                print(f"   Regions: {len(result.get('region_analysis', {}))}")
            
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
    """Test live endpoints"""
    base_url = "http://localhost:8002"
    
    endpoints = [
        ("/stats", "Original Stats"),
        ("/live-stats", "Live Stats (with predictions)"),
        ("/claims-analysis", "Original Claims Analysis"),
        ("/live-claims-analysis", "Live Claims Analysis (with predictions)"),
    ]
    
    print("🧪 Testing Live Dashboard Endpoints")
    print("=" * 60)
    
    results = []
    for endpoint, name in endpoints:
        url = base_url + endpoint
        success = test_endpoint(url, name)
        results.append((name, success))
        print()
    
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = 0
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
        if success:
            passed += 1
    
    print(f"\n🏁 Results: {passed}/{len(results)} endpoints working")
    
    if passed == len(results):
        print("🎉 All live endpoints are working!")
        print("✅ Dashboard will update automatically with user predictions")
    else:
        print("⚠️ Some endpoints failed")

if __name__ == "__main__":
    main()
