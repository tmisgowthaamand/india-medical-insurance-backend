#!/usr/bin/env python3
"""
Test dashboard endpoints to ensure they work properly
"""

import requests
import json

def test_login_and_dashboard():
    """Test login and then dashboard endpoints"""
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    print("🧪 Testing Dashboard Endpoints")
    print("=" * 50)
    
    # Step 1: Test login
    print("1️⃣ Testing login...")
    
    login_data = {
        'username': 'admin@example.com',
        'password': 'admin123'
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Login successful!")
            print(f"   Token: {login_result.get('access_token', 'N/A')[:20]}...")
            
            token = login_result.get('access_token')
            if not token:
                print("❌ No access token received")
                return False
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Test dashboard endpoints with token
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints_to_test = [
        ('/stats', 'Stats endpoint'),
        ('/model-info', 'Model info endpoint'),
        ('/health', 'Health endpoint (no auth needed)')
    ]
    
    results = []
    
    for endpoint, description in endpoints_to_test:
        print(f"\n2️⃣ Testing {description}...")
        
        try:
            # For health endpoint, don't use auth headers
            test_headers = {} if endpoint == '/health' else headers
            
            response = requests.get(
                f"{base_url}{endpoint}",
                headers=test_headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ {description} working!")
                try:
                    data = response.json()
                    print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                    results.append(True)
                except:
                    print(f"   Response: {response.text[:100]}...")
                    results.append(True)
            else:
                print(f"❌ {description} failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {description} error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Login: {'✅ WORKING' if token else '❌ FAILED'}")
    
    for i, (endpoint, description) in enumerate(endpoints_to_test):
        status = '✅ WORKING' if results[i] else '❌ FAILED'
        print(f"{description}: {status}")
    
    all_working = all(results) and bool(token)
    
    if all_working:
        print("\n🎉 All dashboard endpoints are working!")
        print("✅ Login successful")
        print("✅ Authentication working")
        print("✅ Dashboard should load properly")
    else:
        print("\n⚠️ Some endpoints have issues")
        print("This might cause dashboard loading problems")
    
    return all_working

if __name__ == "__main__":
    test_login_and_dashboard()
