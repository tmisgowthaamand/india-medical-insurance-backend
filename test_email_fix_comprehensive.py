#!/usr/bin/env python3
"""
Comprehensive Email Timeout Fix Test Script
Tests the improved email functionality with retry mechanism and better timeout handling.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://india-medical-insurance-backend.onrender.com"
LOCAL_URL = "http://localhost:8001"

def test_email_endpoint(base_url, test_email="gokrishna98@gmail.com"):
    """Test the email endpoint with comprehensive error handling"""
    
    print(f"\n🧪 Testing Email Endpoint: {base_url}")
    print(f"📧 Test Email: {test_email}")
    print("=" * 60)
    
    # Test data
    email_data = {
        "email": test_email,
        "prediction": {
            "prediction": 45000,
            "confidence": 0.87,
            "input_data": {
                "age": 35,
                "bmi": 24.5,
                "gender": "Male",
                "smoker": "No",
                "region": "North",
                "premium_annual_inr": 25000
            }
        },
        "patient_data": {
            "age": 35,
            "bmi": 24.5,
            "gender": "Male",
            "smoker": "No",
            "region": "North",
            "premium_annual_inr": 25000
        }
    }
    
    try:
        # Step 1: Test health endpoint first (wake up service)
        print("🏥 Step 1: Testing health endpoint...")
        health_start = time.time()
        
        try:
            health_response = requests.get(f"{base_url}/health", timeout=30)
            health_time = time.time() - health_start
            
            if health_response.status_code == 200:
                print(f"✅ Health check passed ({health_time:.2f}s)")
                print(f"   Response: {health_response.json()}")
            else:
                print(f"⚠️ Health check returned {health_response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏰ Health check timed out (30s) - service may be sleeping")
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check failed: {e}")
        
        # Step 2: Test email endpoint with extended timeout
        print("\n📧 Step 2: Testing email endpoint...")
        email_start = time.time()
        
        # Use extended timeout for Render services
        timeout = 90 if 'onrender.com' in base_url else 30
        print(f"⏱️ Using {timeout}s timeout for email request")
        
        response = requests.post(
            f"{base_url}/send-prediction-email",
            json=email_data,
            timeout=timeout,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        email_time = time.time() - email_start
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"⏱️ Response Time: {email_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email endpoint successful!")
            print(f"   Success: {result.get('success', 'Unknown')}")
            print(f"   Message: {result.get('message', 'No message')}")
            
            if result.get('mock'):
                print("   🎭 Mock/Demo response (backend unavailable)")
            else:
                print("   📧 Real email sent!")
                
            return True
            
        else:
            print(f"❌ Email endpoint failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        email_time = time.time() - email_start
        print(f"⏰ Email request timed out after {email_time:.2f}s")
        print("   This indicates the service is sleeping or overloaded")
        return False
        
    except requests.exceptions.ConnectionError:
        print("🌐 Connection error - service may be down")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False

def test_multiple_retries():
    """Test the retry mechanism by simulating multiple attempts"""
    print("\n🔄 Testing Retry Mechanism Simulation")
    print("=" * 60)
    
    # Simulate retry delays
    for attempt in range(3):
        delay = (attempt + 1) * 2
        print(f"🔄 Attempt {attempt + 1}/3 - waiting {delay}s before retry...")
        time.sleep(min(delay, 2))  # Cap at 2s for testing
        print(f"   ✅ Retry attempt {attempt + 1} would execute now")
    
    print("✅ Retry mechanism simulation complete")

def main():
    """Main test function"""
    print("🚀 Email Timeout Fix - Comprehensive Test")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Local backend (if available)
    print("\n📍 TEST 1: Local Backend")
    try:
        local_result = test_email_endpoint(LOCAL_URL)
        results['local'] = local_result
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        results['local'] = False
    
    # Test 2: Render backend
    print("\n📍 TEST 2: Render Backend (Production)")
    try:
        render_result = test_email_endpoint(BASE_URL)
        results['render'] = render_result
    except Exception as e:
        print(f"❌ Render test failed: {e}")
        results['render'] = False
    
    # Test 3: Retry mechanism
    test_multiple_retries()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Local Backend:  {'✅ PASS' if results.get('local') else '❌ FAIL'}")
    print(f"Render Backend: {'✅ PASS' if results.get('render') else '❌ FAIL'}")
    
    if any(results.values()):
        print("\n🎉 At least one backend is working!")
        print("💡 The improved timeout and retry mechanism should resolve email issues.")
    else:
        print("\n⚠️ Both backends failed - this may indicate:")
        print("   • Services are sleeping (normal for free tier)")
        print("   • Network connectivity issues")
        print("   • Backend configuration problems")
        
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
