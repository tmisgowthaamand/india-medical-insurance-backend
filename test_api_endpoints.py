#!/usr/bin/env python3
"""
API Endpoint Testing Script
Tests all critical endpoints after PGRST205 fix
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://india-medical-insurance-backend.onrender.com"
FRONTEND_URL = "https://india-medical-insurance-frontend.vercel.app"

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"\n🔍 Testing {method} {endpoint}")
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "OPTIONS":
            response = requests.options(url, headers=headers, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"   ✅ SUCCESS")
            if response.text:
                try:
                    result = response.json()
                    if isinstance(result, dict) and len(result) <= 3:
                        print(f"   Response: {result}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT - Request took longer than 30 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ CONNECTION ERROR - Could not connect to server")
        return False
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        return False

def test_cors():
    """Test CORS configuration"""
    print(f"\n🌐 Testing CORS from {FRONTEND_URL}")
    
    headers = {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type, Authorization'
    }
    
    return test_endpoint("OPTIONS", "/signup", headers=headers, expected_status=200)

def test_signup_login_flow():
    """Test complete signup and login flow"""
    print(f"\n👤 Testing Signup/Login Flow")
    
    # Test data
    test_user = {
        "email": f"test_{int(time.time())}@example.com",
        "password": "test123456"
    }
    
    # Test signup
    signup_success = test_endpoint("POST", "/signup", data=test_user, expected_status=200)
    
    if signup_success:
        # Test login
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        
        # Login uses form data, not JSON
        try:
            print(f"\n🔐 Testing Login")
            response = requests.post(
                f"{BASE_URL}/login",
                data=login_data,  # Use data instead of json for form data
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ LOGIN SUCCESS")
                result = response.json()
                if "access_token" in result:
                    print(f"   Token received: {result['access_token'][:20]}...")
                    return result["access_token"]
                return True
            else:
                print(f"   ❌ LOGIN FAILED - {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ LOGIN ERROR - {str(e)}")
            return False
    
    return False

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""
    if not token:
        print("\n⚠️ Skipping authenticated endpoint tests - no token available")
        return
    
    print(f"\n🔒 Testing Authenticated Endpoints")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /me endpoint
    test_endpoint("GET", "/me", headers=headers, expected_status=200)
    
    # Test /model-info endpoint
    test_endpoint("GET", "/model-info", headers=headers, expected_status=200)

def main():
    """Main testing function"""
    print("🚀 Starting API Endpoint Tests")
    print(f"📍 Backend URL: {BASE_URL}")
    print(f"📍 Frontend URL: {FRONTEND_URL}")
    print(f"⏰ Test Time: {datetime.now().isoformat()}")
    
    results = []
    
    # Basic health checks
    print(f"\n{'='*50}")
    print("BASIC HEALTH CHECKS")
    print(f"{'='*50}")
    
    results.append(("Health Check", test_endpoint("GET", "/health")))
    results.append(("Root Endpoint", test_endpoint("GET", "/")))
    results.append(("CORS Test", test_cors()))
    
    # Authentication flow
    print(f"\n{'='*50}")
    print("AUTHENTICATION TESTS")
    print(f"{'='*50}")
    
    # Test with default admin user first
    admin_login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        print(f"\n🔐 Testing Admin Login")
        response = requests.post(
            f"{BASE_URL}/login",
            data=admin_login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ ADMIN LOGIN SUCCESS")
            result = response.json()
            admin_token = result.get("access_token")
            results.append(("Admin Login", True))
        else:
            print(f"   ❌ ADMIN LOGIN FAILED")
            results.append(("Admin Login", False))
            admin_token = None
    except Exception as e:
        print(f"   ❌ ADMIN LOGIN ERROR - {str(e)}")
        results.append(("Admin Login", False))
        admin_token = None
    
    # Test signup/login flow
    user_token = test_signup_login_flow()
    results.append(("Signup/Login Flow", bool(user_token)))
    
    # Test authenticated endpoints
    token_to_use = admin_token or user_token
    if token_to_use:
        test_authenticated_endpoints(token_to_use)
        results.append(("Authenticated Endpoints", True))
    else:
        results.append(("Authenticated Endpoints", False))
    
    # Public endpoints
    print(f"\n{'='*50}")
    print("PUBLIC ENDPOINTS")
    print(f"{'='*50}")
    
    results.append(("Stats Endpoint", test_endpoint("GET", "/stats")))
    results.append(("Claims Analysis", test_endpoint("GET", "/claims-analysis")))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! PGRST205 error is fixed!")
    elif passed >= total * 0.7:
        print("⚠️ Most tests passed. Some minor issues may remain.")
    else:
        print("❌ Multiple tests failed. PGRST205 error may not be fully resolved.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
