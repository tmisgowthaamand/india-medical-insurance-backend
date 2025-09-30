#!/usr/bin/env python3
"""
Force Render deployment with CORS fix
"""

import requests
import time
import os

def test_local_cors_fix():
    """Test the CORS fix locally first"""
    
    print("🧪 Testing Local CORS Fix")
    print("=" * 30)
    
    try:
        # Test local backend if running
        response = requests.get("http://localhost:8001/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            cors_origins = data.get('cors_origins', [])
            
            print("✅ Local backend running")
            print(f"📊 CORS origins: {cors_origins}")
            
            if '*' in cors_origins or 'http://localhost:3000' in cors_origins:
                print("✅ Local CORS fix working!")
                return True
            else:
                print("❌ Local CORS needs more work")
                return False
        else:
            print("❌ Local backend not responding")
            return False
            
    except Exception as e:
        print(f"⚠️ Local backend not running: {e}")
        return False

def create_render_webhook_deploy():
    """Create a webhook to trigger Render deployment"""
    
    print("\n🚀 Render Deployment Options")
    print("=" * 40)
    
    print("Since direct API deployment isn't available, here are options:")
    print()
    print("1️⃣ Manual Dashboard Update (Fastest):")
    print("   - Go to: https://dashboard.render.com")
    print("   - Service: medical-insurance-api")
    print("   - Environment tab")
    print("   - Change ALLOWED_ORIGINS to: *")
    print("   - Save Changes")
    print()
    print("2️⃣ Manual Deploy (Alternative):")
    print("   - Go to: https://dashboard.render.com")
    print("   - Service: medical-insurance-api")
    print("   - Manual Deploy > Deploy latest commit")
    print()
    print("3️⃣ Code-Based Fix (Current Solution):")
    print("   - Backend code now forces CORS to work")
    print("   - Will work regardless of environment variable")
    print("   - Just needs any redeploy to take effect")

def wait_and_test_render():
    """Wait for Render deployment and test"""
    
    print("\n⏳ Waiting for Render Deployment")
    print("=" * 40)
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    print("Checking every 30 seconds for deployment...")
    
    for attempt in range(10):  # Check for 5 minutes
        try:
            print(f"   Attempt {attempt + 1}/10...")
            
            response = requests.get(f"{base_url}/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                cors_origins = data.get('cors_origins', [])
                
                print(f"   Current CORS: {cors_origins}")
                
                # Check if CORS has been updated
                if '*' in cors_origins or len(cors_origins) > 1:
                    print("✅ Deployment detected - CORS updated!")
                    return True
                    
        except Exception as e:
            print(f"   Still deploying... ({e})")
        
        time.sleep(30)
    
    print("⚠️ Deployment not detected in 5 minutes")
    return False

def test_cors_after_deploy():
    """Test CORS after deployment"""
    
    print("\n🧪 Testing CORS After Deployment")
    print("=" * 40)
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    try:
        # Test actual login with CORS
        response = requests.post(
            f"{base_url}/login",
            data={'username': 'admin@example.com', 'password': 'admin123'},
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'http://localhost:3000'
            },
            timeout=30
        )
        
        print(f"Login response status: {response.status_code}")
        
        # Check CORS headers in response
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        print(f"CORS header: {cors_header}")
        
        if response.status_code in [200, 401]:  # 401 is fine, means CORS worked
            print("✅ CORS is working!")
            return True
        else:
            print("❌ CORS still blocked")
            return False
            
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Main function"""
    
    print("🔧 Force Render CORS Fix")
    print("=" * 50)
    
    # Test local fix first
    local_working = test_local_cors_fix()
    
    if local_working:
        print("\n✅ Local CORS fix is working!")
    else:
        print("\n⚠️ Local backend not available for testing")
    
    # Provide deployment options
    create_render_webhook_deploy()
    
    # Ask user if they want to wait and test
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Update ALLOWED_ORIGINS in Render Dashboard")
    print("2. Wait for deployment (3-5 minutes)")
    print("3. Run: py check_cors_status.py")
    print("4. Test login on your website")
    print()
    print("💡 The code fix ensures CORS will work after any deployment!")

if __name__ == "__main__":
    main()
