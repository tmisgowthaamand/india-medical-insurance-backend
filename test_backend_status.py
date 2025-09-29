#!/usr/bin/env python3
"""
Quick test to check backend status and identify the 500 error
"""

import requests
import json

def test_backend():
    backend_url = "https://india-medical-insurance-backend.onrender.com"
    
    print("🔍 Testing Backend Status")
    print("=" * 40)
    print(f"Backend URL: {backend_url}")
    print()
    
    # Test health endpoint
    print("1. Testing /health endpoint...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            print("   ✅ Backend is healthy")
        else:
            print(f"   ❌ Error Response: {response.text[:500]}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print()
    
    # Test signup endpoint
    print("2. Testing /signup endpoint...")
    try:
        test_data = {"email": "test@example.com", "password": "test123"}
        response = requests.post(
            f"{backend_url}/signup",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
        if response.status_code == 500:
            print("   ❌ 500 Error Confirmed - Database tables missing")
        elif response.status_code == 200:
            print("   ✅ Signup working")
        elif response.status_code == 400 and "already exists" in response.text:
            print("   ✅ Signup working (user exists)")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print()
    print("=" * 40)

if __name__ == "__main__":
    test_backend()
