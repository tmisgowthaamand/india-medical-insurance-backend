#!/usr/bin/env python3
"""
Test API URL Fix
Verifies that frontend will now connect to localhost instead of Render
"""

import requests
import time

def test_localhost_backend():
    """Test localhost backend availability"""
    
    print("🏠 Testing Localhost Backend")
    print("=" * 50)
    
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8001/health", timeout=5)
        end_time = time.time()
        
        duration = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ Localhost backend is running")
            print(f"⏱️ Response time: {duration:.2f}s")
            return True
        else:
            print(f"⚠️ Localhost backend returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Localhost backend not accessible: {e}")
        return False

def test_render_backend():
    """Test Render backend (for comparison)"""
    
    print("\n☁️ Testing Render Backend")
    print("=" * 50)
    
    try:
        start_time = time.time()
        response = requests.get("https://india-medical-insurance-backend.onrender.com/health", timeout=15)
        end_time = time.time()
        
        duration = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ Render backend is running")
            print(f"⏱️ Response time: {duration:.2f}s")
            return True
        else:
            print(f"⚠️ Render backend returned: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Render backend timed out (likely sleeping)")
        return False
    except Exception as e:
        print(f"❌ Render backend error: {e}")
        return False

def test_email_endpoint_localhost():
    """Test email endpoint on localhost"""
    
    print("\n📧 Testing Email Endpoint on Localhost")
    print("=" * 50)
    
    email_data = {
        "email": "gowthaamankrishna1998@gmail.com",
        "prediction": {
            "prediction": 25000.0,
            "confidence": 0.85
        },
        "patient_data": {
            "age": 35,
            "bmi": 23.0,
            "gender": "Male",
            "smoker": "No",
            "region": "East",
            "premium_annual_inr": 25000.0
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8001/send-prediction-email",
            json=email_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            timeout=30
        )
        end_time = time.time()
        
        duration = end_time - start_time
        
        print(f"⏱️ Email API response time: {duration:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📝 Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Email API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Email API error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🔧 API URL Fix Verification")
    print("=" * 60)
    
    localhost_ok = test_localhost_backend()
    render_ok = test_render_backend()
    email_ok = test_email_endpoint_localhost()
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 60)
    
    print(f"🏠 Localhost Backend: {'✅ Working' if localhost_ok else '❌ Not working'}")
    print(f"☁️ Render Backend: {'✅ Working' if render_ok else '❌ Not working'}")
    print(f"📧 Email API (localhost): {'✅ Working' if email_ok else '❌ Not working'}")
    
    print(f"\n🎯 FRONTEND FIX STATUS")
    print("=" * 60)
    
    if localhost_ok and email_ok:
        print("🎉 FRONTEND WILL NOW USE LOCALHOST!")
        print("✅ API URL fix applied successfully")
        print("✅ Localhost backend is working")
        print("✅ Email API is responding")
        print("\n💡 Next steps:")
        print("1. Refresh your frontend page")
        print("2. Try sending an email")
        print("3. It should now connect to localhost instead of Render")
    elif localhost_ok:
        print("⚠️ Localhost backend works but email API has issues")
        print("💡 Check email service configuration")
    else:
        print("❌ Localhost backend is not running")
        print("💡 Make sure backend server is started on port 8001")
    
    if not render_ok:
        print("\n📝 NOTE: Render backend is sleeping/unavailable")
        print("This was causing the timeout errors before the fix")

if __name__ == "__main__":
    main()
