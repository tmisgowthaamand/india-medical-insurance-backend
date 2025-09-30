#!/usr/bin/env python3
"""
Test login credentials and backend connectivity
"""

import requests
import json

def test_backend_connectivity():
    """Test if backend is accessible and login works"""
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    print("🧪 Testing Backend Connectivity & Login")
    print("=" * 60)
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Model loaded: {health_data.get('model_loaded')}")
            print(f"   CORS origins: {health_data.get('cors_origins')}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: CORS preflight
    print("\n2️⃣ Testing CORS preflight...")
    try:
        cors_response = requests.options(
            f"{base_url}/login",
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        print(f"   CORS preflight status: {cors_response.status_code}")
        print(f"   CORS headers: {dict(cors_response.headers)}")
    except Exception as e:
        print(f"⚠️ CORS preflight error: {e}")
    
    # Test 3: Login with different credentials
    credentials_to_test = [
        ("admin@example.com", "admin123"),
        ("user@example.com", "user123"),
        ("demo@example.com", "demo123")
    ]
    
    print("\n3️⃣ Testing login credentials...")
    
    for email, password in credentials_to_test:
        print(f"\n   Testing: {email} / {password}")
        
        try:
            login_data = {
                'username': email,
                'password': password
            }
            
            login_response = requests.post(
                f"{base_url}/login",
                data=login_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'http://localhost:3000'
                },
                timeout=30
            )
            
            if login_response.status_code == 200:
                result = login_response.json()
                print(f"   ✅ Login successful!")
                print(f"      Token: {result.get('access_token', 'N/A')[:20]}...")
                print(f"      Email: {result.get('email')}")
                print(f"      Is Admin: {result.get('is_admin')}")
                return True
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                try:
                    error_data = login_response.json()
                    print(f"      Error: {error_data}")
                except:
                    print(f"      Response: {login_response.text}")
                    
        except Exception as e:
            print(f"   ❌ Login error: {e}")
    
    # Test 4: Check if we can create a user via signup
    print("\n4️⃣ Testing signup to create a test user...")
    
    try:
        signup_data = {
            'email': 'test@example.com',
            'password': 'test123'
        }
        
        signup_response = requests.post(
            f"{base_url}/signup",
            json=signup_data,
            headers={
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000'
            },
            timeout=30
        )
        
        if signup_response.status_code == 200:
            print("   ✅ Signup successful - can create users")
            
            # Now try to login with the new user
            print("   🔄 Testing login with new user...")
            login_data = {
                'username': 'test@example.com',
                'password': 'test123'
            }
            
            login_response = requests.post(
                f"{base_url}/login",
                data=login_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'http://localhost:3000'
                },
                timeout=30
            )
            
            if login_response.status_code == 200:
                print("   ✅ Login with new user successful!")
                return True
            else:
                print(f"   ❌ Login with new user failed: {login_response.status_code}")
                
        else:
            print(f"   ❌ Signup failed: {signup_response.status_code}")
            try:
                error_data = signup_response.json()
                print(f"      Error: {error_data}")
            except:
                print(f"      Response: {signup_response.text}")
                
    except Exception as e:
        print(f"   ❌ Signup error: {e}")
    
    return False

def main():
    """Main test function"""
    success = test_backend_connectivity()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Backend is working! Login credentials are valid.")
        print("✅ Frontend should be able to connect successfully")
    else:
        print("❌ Backend connectivity issues detected")
        print("⚠️ This explains the 'Cannot connect to server' error")
        print("\n💡 Possible solutions:")
        print("   1. Check if Render service is running")
        print("   2. Verify CORS configuration")
        print("   3. Check if default users exist")
        print("   4. Verify environment variables")

if __name__ == "__main__":
    main()
