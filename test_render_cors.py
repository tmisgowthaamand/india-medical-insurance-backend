#!/usr/bin/env python3
"""
Test Render CORS configuration after deployment
"""

import requests
import time
import json

def test_render_cors():
    """Test CORS configuration on Render"""
    
    print("🧪 Testing Render CORS Configuration")
    print("=" * 50)
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    # Test 1: Health endpoint
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   Status: {data.get('status')}")
            print(f"   CORS Origins: {data.get('cors_origins')}")
            
            cors_origins = data.get('cors_origins', [])
            if '*' in cors_origins or 'http://localhost:3000' in cors_origins:
                print("✅ CORS includes localhost support")
            else:
                print("❌ CORS missing localhost support")
                print(f"   Current: {cors_origins}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test 2: CORS preflight for login
    print("\n2️⃣ Testing CORS preflight for login...")
    try:
        response = requests.options(
            f"{base_url}/login",
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        print(f"   Preflight status: {response.status_code}")
        
        # Check CORS headers
        allow_origin = response.headers.get('Access-Control-Allow-Origin')
        allow_methods = response.headers.get('Access-Control-Allow-Methods')
        allow_headers = response.headers.get('Access-Control-Allow-Headers')
        allow_credentials = response.headers.get('Access-Control-Allow-Credentials')
        
        print(f"   Allow-Origin: {allow_origin}")
        print(f"   Allow-Methods: {allow_methods}")
        print(f"   Allow-Headers: {allow_headers}")
        print(f"   Allow-Credentials: {allow_credentials}")
        
        if allow_origin in ['*', 'http://localhost:3000']:
            print("✅ CORS preflight allows localhost")
        else:
            print("❌ CORS preflight blocks localhost")
            return False
            
    except Exception as e:
        print(f"❌ CORS preflight error: {e}")
        return False
    
    # Test 3: Actual login test
    print("\n3️⃣ Testing actual login with CORS...")
    try:
        login_data = {
            'username': 'admin@example.com',
            'password': 'admin123'
        }
        
        response = requests.post(
            f"{base_url}/login",
            data=login_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'http://localhost:3000'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful with CORS!")
            print(f"   Email: {result.get('email')}")
            print(f"   Is Admin: {result.get('is_admin')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def wait_for_deployment():
    """Wait for Render deployment to complete"""
    
    print("⏳ Waiting for Render deployment...")
    print("This usually takes 5-10 minutes")
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    for attempt in range(20):  # Wait up to 20 minutes
        try:
            print(f"   Attempt {attempt + 1}/20...")
            response = requests.get(f"{base_url}/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                cors_origins = data.get('cors_origins', [])
                
                # Check if CORS has been updated
                if '*' in cors_origins or 'http://localhost:3000' in cors_origins:
                    print("✅ Deployment complete - CORS updated!")
                    return True
                else:
                    print(f"   Still old CORS: {cors_origins}")
            
        except Exception as e:
            print(f"   Deployment still in progress... ({e})")
        
        time.sleep(30)  # Wait 30 seconds between checks
    
    print("⚠️ Deployment taking longer than expected")
    return False

def main():
    """Main test function"""
    
    print("🔧 Render CORS Fix Verification")
    print("=" * 60)
    
    # First check current status
    print("📊 Checking current deployment status...")
    current_working = test_render_cors()
    
    if current_working:
        print("\n🎉 CORS is already working!")
        print("✅ You can now use the Render backend from localhost")
    else:
        print("\n⏳ CORS not working yet - checking if deployment is in progress...")
        
        # Wait for deployment
        deployment_complete = wait_for_deployment()
        
        if deployment_complete:
            print("\n🧪 Testing CORS after deployment...")
            final_working = test_render_cors()
            
            if final_working:
                print("\n🎉 CORS fix successful!")
                print("✅ Render backend now works from localhost")
            else:
                print("\n❌ CORS still not working after deployment")
        else:
            print("\n⚠️ Deployment not detected - manual check needed")
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("If CORS is working:")
    print("  1. Update frontend .env to use Render URL")
    print("  2. Test login from your website")
    print("  3. Dashboard should load properly")
    print()
    print("If CORS still not working:")
    print("  1. Check Render Dashboard for deployment status")
    print("  2. Manually trigger redeploy if needed")
    print("  3. Verify environment variables in Render")

if __name__ == "__main__":
    main()
