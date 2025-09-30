#!/usr/bin/env python3
"""
Test favicon and error fixes
"""

import requests
import time

def test_endpoints():
    """Test various endpoints to ensure no 405 errors"""
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    test_cases = [
        {"path": "/", "expected": 200, "description": "Root endpoint"},
        {"path": "/health", "expected": 200, "description": "Health check"},
        {"path": "/favicon.ico", "expected": 204, "description": "Favicon (should not be 405)"},
        {"path": "/robots.txt", "expected": 204, "description": "Robots.txt"},
        {"path": "/nonexistent", "expected": 200, "description": "Catch-all handler"},
    ]
    
    print("🔍 Testing Render Backend Endpoints")
    print("=" * 50)
    
    results = []
    
    for test in test_cases:
        try:
            print(f"Testing {test['path']}...")
            response = requests.get(f"{base_url}{test['path']}", timeout=10)
            
            if response.status_code == test['expected']:
                print(f"✅ {test['description']}: {response.status_code}")
                results.append(True)
            else:
                print(f"❌ {test['description']}: Expected {test['expected']}, got {response.status_code}")
                results.append(False)
                
            # Show response for debugging
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    print(f"   Response: {response.json()}")
                else:
                    print(f"   Response: {response.text[:100]}...")
            except:
                print(f"   Response: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⚠️ {test['description']}: Timeout (cold start)")
            results.append(False)
        except Exception as e:
            print(f"❌ {test['description']}: Error - {e}")
            results.append(False)
        
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All endpoints working correctly!")
    else:
        print("⚠️ Some endpoints need attention")
    
    return passed == total

if __name__ == "__main__":
    test_endpoints()
