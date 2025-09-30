#!/usr/bin/env python3
"""
Deploy backend to Render with updated CORS configuration
"""

import os
import subprocess
import requests
import time

def check_render_deployment():
    """Check if Render deployment is working"""
    
    print("🔍 Checking Render Deployment")
    print("=" * 40)
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    # Test health endpoint
    try:
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   CORS Origins: {data.get('cors_origins')}")
            
            # Check if localhost is in CORS origins
            cors_origins = data.get('cors_origins', [])
            if 'http://localhost:3000' in cors_origins or '*' in cors_origins:
                print("✅ CORS configured for localhost")
                return True
            else:
                print("❌ CORS not configured for localhost")
                print(f"   Current origins: {cors_origins}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_cors_from_localhost():
    """Test CORS from localhost perspective"""
    
    print("\n2️⃣ Testing CORS from localhost...")
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    # Test CORS preflight
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
        
        print(f"   CORS preflight status: {response.status_code}")
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print("   CORS Headers:")
        for header, value in cors_headers.items():
            if value:
                print(f"      {header}: {value}")
        
        # Check if Origin is allowed
        allowed_origin = response.headers.get('Access-Control-Allow-Origin')
        if allowed_origin in ['*', 'http://localhost:3000']:
            print("✅ CORS allows localhost:3000")
            return True
        else:
            print(f"❌ CORS doesn't allow localhost:3000 (got: {allowed_origin})")
            return False
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def provide_deployment_instructions():
    """Provide instructions for manual deployment"""
    
    print("\n📋 Manual Deployment Instructions")
    print("=" * 40)
    print("Since automatic deployment isn't available, please:")
    print()
    print("1️⃣ Commit your changes:")
    print("   git add .")
    print("   git commit -m 'Fix CORS configuration for localhost'")
    print("   git push origin main")
    print()
    print("2️⃣ In Render Dashboard:")
    print("   - Go to your service: medical-insurance-api")
    print("   - Click 'Manual Deploy' > 'Deploy latest commit'")
    print("   - Wait for deployment to complete (~5-10 minutes)")
    print()
    print("3️⃣ Verify deployment:")
    print("   - Check health endpoint responds")
    print("   - Verify CORS origins include localhost")
    print("   - Test login from frontend")
    print()
    print("4️⃣ Alternative - Update Environment Variable:")
    print("   - In Render Dashboard > Environment")
    print("   - Set ALLOWED_ORIGINS = *")
    print("   - Click 'Save Changes'")
    print("   - Service will auto-redeploy")

def main():
    """Main function"""
    
    print("🚀 Render Deployment Helper")
    print("=" * 50)
    
    # Check current deployment status
    is_working = check_render_deployment()
    cors_working = test_cors_from_localhost()
    
    print("\n" + "=" * 50)
    print("📊 Current Status:")
    print(f"Health Endpoint: {'✅ WORKING' if is_working else '❌ ISSUES'}")
    print(f"CORS for localhost: {'✅ WORKING' if cors_working else '❌ BLOCKED'}")
    
    if is_working and cors_working:
        print("\n🎉 Render deployment is working correctly!")
        print("✅ You can now test login from localhost:3000")
    else:
        print("\n⚠️ Render deployment needs updating")
        provide_deployment_instructions()
        
        print("\n💡 Quick Fix - Test with local backend:")
        print("   1. Keep local backend running (py -m uvicorn app:app --port 8001)")
        print("   2. Update frontend .env to use http://localhost:8001")
        print("   3. Test login - should work immediately")

if __name__ == "__main__":
    main()
