#!/usr/bin/env python3
"""
Test HEAD Request Support
Verifies that the backend properly handles HEAD requests for health checks
"""

import requests
import sys
from datetime import datetime

def test_head_requests():
    """Test HEAD requests to various endpoints"""
    
    print("🔍 Testing HEAD Request Support")
    print("=" * 50)
    
    # Test endpoints
    base_url = "https://india-medical-insurance-backend.onrender.com"
    endpoints = [
        "/",
        "/health",
        "/cors-test"
    ]
    
    all_passed = True
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing HEAD {endpoint}")
        
        try:
            # Test HEAD request
            head_response = requests.head(url, timeout=30)
            print(f"   Status Code: {head_response.status_code}")
            print(f"   Headers: {dict(head_response.headers)}")
            
            if head_response.status_code == 200:
                print("   ✅ HEAD request successful")
            elif head_response.status_code == 405:
                print("   ❌ Method Not Allowed (405) - HEAD not supported")
                all_passed = False
            else:
                print(f"   ⚠️ Unexpected status code: {head_response.status_code}")
                all_passed = False
            
            # Compare with GET request for reference
            print(f"   🔄 Comparing with GET request...")
            get_response = requests.get(url, timeout=30)
            print(f"   GET Status: {get_response.status_code}")
            
            if head_response.status_code == get_response.status_code:
                print("   ✅ HEAD and GET status codes match")
            else:
                print(f"   ⚠️ Status code mismatch - HEAD: {head_response.status_code}, GET: {get_response.status_code}")
            
        except requests.exceptions.Timeout:
            print("   ❌ Request timed out")
            all_passed = False
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection error")
            all_passed = False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All HEAD request tests passed!")
        print("✅ 405 Method Not Allowed error should be resolved")
    else:
        print("❌ Some HEAD request tests failed")
        print("⚠️ You may need to redeploy the backend service")
    
    return all_passed

def test_local_server():
    """Test HEAD requests against local development server"""
    
    print("\n🏠 Testing Local Development Server")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoints = ["/", "/health"]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing HEAD {endpoint} (local)")
        
        try:
            head_response = requests.head(url, timeout=5)
            print(f"   Status Code: {head_response.status_code}")
            
            if head_response.status_code == 200:
                print("   ✅ Local HEAD request successful")
            else:
                print(f"   ❌ Local HEAD request failed: {head_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ⚠️ Local server not running (this is normal if not started)")
        except Exception as e:
            print(f"   ❌ Local test error: {e}")

if __name__ == "__main__":
    print(f"🕐 Test started at: {datetime.now().isoformat()}")
    
    # Test production server
    production_success = test_head_requests()
    
    # Test local server (optional)
    test_local_server()
    
    print(f"\n📋 Summary:")
    print(f"   Production HEAD support: {'✅ Working' if production_success else '❌ Failed'}")
    print(f"   Time: {datetime.now().isoformat()}")
    
    if production_success:
        print(f"\n🚀 Next steps:")
        print(f"   1. The 405 Method Not Allowed error should be resolved")
        print(f"   2. Render health checks should work properly")
        print(f"   3. Monitor your Render logs for confirmation")
        sys.exit(0)
    else:
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Make sure you've deployed the updated backend code")
        print(f"   2. Check Render deployment logs for any errors")
        print(f"   3. Verify the service is running properly")
        sys.exit(1)
