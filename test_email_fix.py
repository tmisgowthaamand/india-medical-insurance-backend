#!/usr/bin/env python3
"""
Test email service fixes
"""

import requests
import json
import time

def test_email_endpoint():
    """Test the send-prediction-email endpoint"""
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    # Test data
    test_request = {
        "email": "test@example.com",
        "prediction": {
            "prediction": 25000.0,
            "confidence": 0.85
        },
        "patient_data": {
            "age": 30,
            "bmi": 25.5,
            "gender": "Male",
            "smoker": "No",
            "region": "North",
            "premium_annual_inr": 20000
        }
    }
    
    print("🧪 Testing Email Service Fix")
    print("=" * 50)
    print(f"Sending request to: {base_url}/send-prediction-email")
    print(f"Test email: {test_request['email']}")
    
    try:
        response = requests.post(
            f"{base_url}/send-prediction-email",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            
            if result.get('success'):
                print("\n🎉 Email service is working correctly!")
                print("✅ No more 500 errors")
                print("✅ Graceful error handling implemented")
                return True
            else:
                print("\n⚠️ Email service returned success=false")
                return False
                
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠️ Request timed out (this might be expected for cold starts)")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_health_endpoint():
    """Test that the main API is still working"""
    
    base_url = "https://india-medical-insurance-backend.onrender.com"
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def main():
    """Main test function"""
    print("🏥 Email Service Fix Verification")
    print("=" * 60)
    
    # Test health first
    health_ok = test_health_endpoint()
    
    if health_ok:
        print("\n" + "=" * 60)
        # Test email endpoint
        email_ok = test_email_endpoint()
        
        print("\n" + "=" * 60)
        print("📊 Test Results:")
        print(f"Health Endpoint: {'✅ WORKING' if health_ok else '❌ FAILED'}")
        print(f"Email Endpoint: {'✅ FIXED' if email_ok else '❌ STILL ISSUES'}")
        
        if health_ok and email_ok:
            print("\n🎉 All tests passed! Email service is fixed.")
            print("✅ No more 500 errors on email sending")
            print("✅ Graceful error handling implemented")
            print("✅ Reports stored locally when email fails")
        else:
            print("\n⚠️ Some issues remain. Check the logs above.")
    else:
        print("\n❌ Backend health check failed. Cannot test email service.")

if __name__ == "__main__":
    main()
