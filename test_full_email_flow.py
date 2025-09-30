#!/usr/bin/env python3
"""
Test Full Email Flow - End-to-End Email Testing
Tests the complete email functionality from API call to delivery
"""

import requests
import json
import time
from datetime import datetime

def test_email_api_endpoint():
    """Test the email API endpoint directly"""
    print("🧪 TESTING EMAIL API ENDPOINT")
    print("=" * 50)
    
    # Test data
    test_request = {
        "email": "gokrishna98@gmail.com",
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
    
    # API endpoint
    api_url = "http://localhost:8001/send-prediction-email"
    
    try:
        print(f"📡 Sending POST request to: {api_url}")
        print(f"📧 Recipient: {test_request['email']}")
        
        response = requests.post(
            api_url,
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                print("🎉 Email API call successful!")
                print(f"📧 Message: {result.get('message')}")
                return True
            else:
                print("❌ Email API returned success=False")
                print(f"📧 Message: {result.get('message')}")
                return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Backend server not running")
        print("💡 Start the backend server with: uvicorn app:app --reload --port 8001")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Server took too long to respond")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_backend_server_status():
    """Test if backend server is running"""
    print("\n🔍 TESTING BACKEND SERVER STATUS")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        print(f"✅ Backend server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("💡 Start with: uvicorn app:app --reload --port 8001")
        return False
    except Exception as e:
        print(f"⚠️ Server status check failed: {e}")
        return False

def test_email_service_directly():
    """Test email service directly"""
    print("\n📧 TESTING EMAIL SERVICE DIRECTLY")
    print("=" * 50)
    
    try:
        from email_service import email_service
        
        test_prediction = {
            "prediction": 25000.0,
            "confidence": 0.85
        }
        
        test_patient_data = {
            "age": 30,
            "bmi": 25.5,
            "gender": "Male",
            "smoker": "No",
            "region": "North",
            "premium_annual_inr": 20000
        }
        
        print("📧 Sending email via email service...")
        success = email_service.send_prediction_email(
            recipient_email="gokrishna98@gmail.com",
            prediction_data=test_prediction,
            patient_data=test_patient_data
        )
        
        if success:
            print("✅ Email service test successful!")
            return True
        else:
            print("❌ Email service test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        return False

def main():
    """Main testing function"""
    print("🧪 FULL EMAIL FLOW TESTING")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 60)
    
    # Test 1: Backend Server Status
    server_running = test_backend_server_status()
    
    # Test 2: Email Service Direct Test
    email_service_ok = test_email_service_directly()
    
    # Test 3: API Endpoint Test (only if server is running)
    api_test_ok = False
    if server_running:
        api_test_ok = test_email_api_endpoint()
    
    # Summary
    print("\n📋 TESTING SUMMARY")
    print("=" * 50)
    print(f"Backend Server: {'✅ RUNNING' if server_running else '❌ NOT RUNNING'}")
    print(f"Email Service: {'✅ OK' if email_service_ok else '❌ FAILED'}")
    print(f"API Endpoint: {'✅ OK' if api_test_ok else '❌ FAILED' if server_running else '⏸️ SKIPPED'}")
    
    if email_service_ok and api_test_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("📧 Email functionality is working correctly")
        print("\n📱 CHECK YOUR EMAIL:")
        print("   1. Check inbox for: gokrishna98@gmail.com")
        print("   2. Check spam/junk folder")
        print("   3. Check promotions tab (Gmail)")
        print("   4. Wait 1-2 minutes for delivery")
    elif email_service_ok and not server_running:
        print("\n⚠️ Email service works, but backend server is not running")
        print("💡 Start backend server to test full API flow")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")

if __name__ == "__main__":
    main()
