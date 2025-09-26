#!/usr/bin/env python3
"""
Test script to verify API endpoints are working correctly
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8001"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def test_api_endpoints():
    """Test various API endpoints to verify they're working"""
    print("Testing API endpoints...")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✓ Root endpoint working")
    except Exception as e:
        print(f"   ✗ Root endpoint failed: {e}")
        return False
    
    # Test 2: Login
    print("\n2. Testing login...")
    try:
        login_data = {
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("   ✓ Login successful")
        else:
            print(f"   ✗ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Login failed: {e}")
        return False
    
    # Headers for authenticated requests
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Stats endpoint (used by refresh)
    print("\n3. Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total policies: {stats.get('total_policies', 'N/A')}")
            print("   ✓ Stats endpoint working")
        else:
            print(f"   ✗ Stats failed: {response.text}")
    except Exception as e:
        print(f"   ✗ Stats failed: {e}")
    
    # Test 4: Model info endpoint (used by refresh)
    print("\n4. Testing model-info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/model-info", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            model_info = response.json()
            print(f"   Model status: {model_info.get('status', 'N/A')}")
            print("   ✓ Model info endpoint working")
        else:
            print(f"   ✗ Model info failed: {response.text}")
    except Exception as e:
        print(f"   ✗ Model info failed: {e}")
    
    # Test 5: Claims analysis endpoint
    print("\n5. Testing claims-analysis endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/claims-analysis", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Claims analysis endpoint working")
        else:
            print(f"   ✗ Claims analysis failed: {response.text}")
    except Exception as e:
        print(f"   ✗ Claims analysis failed: {e}")
    
    print("\n" + "=" * 50)
    print("API endpoint tests completed!")
    return True

if __name__ == "__main__":
    test_api_endpoints()
