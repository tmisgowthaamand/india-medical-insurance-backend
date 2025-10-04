#!/usr/bin/env python3
"""
Check Render Environment Variables
Verifies that all required environment variables are set correctly on Render
"""

import requests
import json

def check_render_environment():
    """Check if Render service has correct environment variables"""
    print("🔍 CHECKING RENDER ENVIRONMENT VARIABLES")
    print("="*60)
    
    render_url = "https://india-medical-insurance-backend.onrender.com"
    
    # Test environment endpoint (if it exists)
    try:
        print("1. Testing environment status...")
        response = requests.get(f"{render_url}/health", timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            print("   ✅ Health endpoint working")
            print(f"   📊 Response: {json.dumps(health_data, indent=2)}")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test email service configuration
    try:
        print("\n2. Testing email service configuration...")
        response = requests.post(
            f"{render_url}/test-email",
            json={"email": "test@example.com"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Email test endpoint working")
            print(f"   📊 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Email test failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Email test error: {e}")
    
    print("\n" + "="*60)
    print("🔧 REQUIRED ENVIRONMENT VARIABLES FOR RENDER:")
    print("="*60)
    print("GMAIL_EMAIL=gokrishna98@gmail.com")
    print("GMAIL_APP_PASSWORD=lwkvzupqanxvafrm")
    print("SUPABASE_URL=your_supabase_url")
    print("SUPABASE_SERVICE_ROLE_KEY=your_service_role_key")
    print("JWT_SECRET_KEY=your_jwt_secret")
    print("ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000")
    print("ENVIRONMENT=production")
    print("\n💡 Make sure these are set in your Render service environment variables!")

if __name__ == "__main__":
    check_render_environment()
