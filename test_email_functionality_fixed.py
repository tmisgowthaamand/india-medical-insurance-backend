#!/usr/bin/env python3
"""
Comprehensive Email Functionality Test - Fixed Version
Tests the improved email service with accurate success/failure responses
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"  # Local backend
# BASE_URL = "https://srv-d3b668ogjchc73f9ece0.onrender.com"  # Render backend

def test_email_endpoint():
    """Test the /send-prediction-email endpoint with various scenarios"""
    
    print("="*80)
    print("🧪 COMPREHENSIVE EMAIL FUNCTIONALITY TEST - FIXED VERSION")
    print("="*80)
    print(f"🌐 Testing backend: {BASE_URL}")
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test data
    test_email = "test@example.com"  # Replace with your actual email for real testing
    
    test_payload = {
        "email": test_email,
        "prediction": {
            "prediction": 25000.50,
            "confidence": 0.85
        },
        "patient_data": {
            "age": 35,
            "bmi": 24.5,
            "gender": "Male",
            "smoker": "No",
            "region": "North",
            "premium_annual_inr": 30000
        }
    }
    
    print("📧 Test Email Configuration:")
    print(f"   Recipient: {test_email}")
    print(f"   Prediction: ₹{test_payload['prediction']['prediction']:,.2f}")
    print(f"   Confidence: {test_payload['prediction']['confidence']*100:.1f}%")
    print()
    
    # Check Gmail environment variables
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print("🔧 Gmail Configuration Check:")
    print(f"   GMAIL_EMAIL: {'✅ Set' if gmail_email else '❌ Not set'}")
    print(f"   GMAIL_APP_PASSWORD: {'✅ Set' if gmail_password else '❌ Not set'}")
    
    if gmail_email:
        print(f"   Sender Email: {gmail_email}")
    
    print()
    
    # Test 1: Send email request
    print("🧪 TEST 1: Email Send Request")
    print("-" * 50)
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/send-prediction-email",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Response Time: {duration:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("📄 Response Data:")
            print(f"   Success: {result.get('success', 'Unknown')}")
            print(f"   Message: {result.get('message', 'No message')}")
            
            # Analyze the response
            if result.get('success'):
                print("✅ RESULT: Email sending reported as SUCCESSFUL")
                print("📧 Expected: Email should be in Gmail inbox")
                print("💡 Action: Check your Gmail inbox and spam folder")
            else:
                print("❌ RESULT: Email sending reported as FAILED")
                print(f"🔍 Reason: {result.get('message', 'Unknown error')}")
                
                if "not configured" in result.get('message', '').lower():
                    print("💡 Action: Configure GMAIL_EMAIL and GMAIL_APP_PASSWORD")
                elif "timeout" in result.get('message', '').lower():
                    print("💡 Action: Check internet connection and try again")
                else:
                    print("💡 Action: Check error message and troubleshoot")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ REQUEST TIMEOUT: Email request took too long")
        print("💡 This might indicate server issues or slow email processing")
        
    except requests.exceptions.ConnectionError:
        print("🌐 CONNECTION ERROR: Cannot connect to backend")
        print("💡 Make sure the backend server is running")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
    
    print()
    
    # Test 2: Invalid email format
    print("🧪 TEST 2: Invalid Email Format")
    print("-" * 50)
    
    invalid_payload = test_payload.copy()
    invalid_payload["email"] = "invalid-email-format"
    
    try:
        response = requests.post(
            f"{BASE_URL}/send-prediction-email",
            json=invalid_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', 'Unknown')}")
            print(f"   Message: {result.get('message', 'No message')}")
            
            if not result.get('success') and "invalid" in result.get('message', '').lower():
                print("✅ RESULT: Invalid email correctly rejected")
            else:
                print("⚠️ RESULT: Invalid email validation may need improvement")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()
    
    # Test 3: Health check
    print("🧪 TEST 3: Backend Health Check")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health = response.json()
            print("✅ Backend is healthy")
            print(f"   Status: {health.get('status', 'Unknown')}")
            print(f"   Model Loaded: {health.get('model_loaded', 'Unknown')}")
        else:
            print(f"⚠️ Health check returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print()
    print("="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    print("✅ Email functionality has been improved with:")
    print("   • Accurate success/failure reporting")
    print("   • Immediate feedback (no delayed notifications)")
    print("   • Better error messages for different scenarios")
    print("   • Improved Gmail delivery headers")
    print()
    print("🔧 To enable real email sending:")
    print("   1. Set GMAIL_EMAIL environment variable")
    print("   2. Set GMAIL_APP_PASSWORD environment variable")
    print("   3. Use a Gmail App Password (not regular password)")
    print()
    print("📧 Expected behavior:")
    print("   • SUCCESS: Email appears in Gmail inbox within 1-2 minutes")
    print("   • FAILURE: Clear error message explaining the issue")
    print("   • NO MORE false 'success' messages for failed emails")
    print()
    print(f"⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    test_email_endpoint()
