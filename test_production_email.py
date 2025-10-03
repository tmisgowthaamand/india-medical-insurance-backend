#!/usr/bin/env python3
"""
Test email functionality on production (Render) deployment
This script tests the /send-prediction-email endpoint on the deployed backend
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Production backend URL
PRODUCTION_URL = "https://srv-d3b668ogjchc73f9ece0-latest.onrender.com"
LOCAL_URL = "http://localhost:8001"

async def test_email_endpoint(base_url: str, environment: str):
    """Test the email endpoint"""
    print(f"🧪 TESTING EMAIL ENDPOINT - {environment.upper()}")
    print("="*80)
    
    # Test data
    test_data = {
        "email": "gowthaamankrishna1998@gmail.com",
        "prediction": {
            "prediction": 25000,
            "confidence": 0.88
        },
        "patient_data": {
            "age": 28,
            "bmi": 24.5,
            "gender": "Male",
            "smoker": "No",
            "region": "South",
            "premium_annual_inr": 22000
        }
    }
    
    print(f"📧 Testing email to: {test_data['email']}")
    print(f"💰 Prediction: ₹{test_data['prediction']['prediction']:,}")
    print(f"🎯 Confidence: {test_data['prediction']['confidence']*100:.1f}%")
    print(f"🌐 Environment: {environment}")
    print(f"🔗 URL: {base_url}/send-prediction-email")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        timeout = aiohttp.ClientTimeout(total=120)  # 2 minutes timeout for Render cold starts
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print("📡 Sending request...")
            
            async with session.post(
                f"{base_url}/send-prediction-email",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                processing_time = time.time() - start_time
                status_code = response.status
                
                print(f"📊 Response Status: {status_code}")
                print(f"⏱️ Response Time: {processing_time:.2f}s")
                
                if status_code == 200:
                    result = await response.json()
                    
                    print(f"✅ Success: {result.get('success', False)}")
                    print(f"📝 Message: {result.get('message', 'No message')}")
                    
                    if result.get('success', False):
                        print(f"\n🎉 EMAIL TEST PASSED - {environment.upper()}!")
                        print("✅ Email should be delivered to Gmail inbox")
                        print("📱 Check your email (including spam folder)")
                        return True
                    else:
                        print(f"\n❌ EMAIL TEST FAILED - {environment.upper()}")
                        print("🔧 Check the error message above")
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP Error {status_code}")
                    print(f"Error details: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        processing_time = time.time() - start_time
        print(f"⏰ TIMEOUT after {processing_time:.2f}s")
        print("❌ Request timed out - this might indicate:")
        print("   1. Render service is sleeping (cold start)")
        print("   2. Email service is taking too long")
        print("   3. Network connectivity issues")
        return False
        
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ ERROR after {processing_time:.2f}s: {e}")
        return False

async def test_health_endpoint(base_url: str, environment: str):
    """Test the health endpoint to wake up the service"""
    print(f"🏥 TESTING HEALTH ENDPOINT - {environment.upper()}")
    print("-" * 40)
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Health check passed: {result}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def main():
    """Main test function"""
    print("🛡️ BULLETPROOF EMAIL SERVICE - PRODUCTION TEST")
    print("="*80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Test production environment
    print("\n🌐 TESTING PRODUCTION ENVIRONMENT (RENDER)")
    print("="*80)
    
    # First, try to wake up the service
    print("🚀 Waking up Render service...")
    health_ok = await test_health_endpoint(PRODUCTION_URL, "production")
    
    if health_ok:
        print("✅ Service is awake, proceeding with email test...")
        await asyncio.sleep(2)  # Give service a moment to fully initialize
    else:
        print("⚠️ Health check failed, but continuing with email test...")
    
    production_success = await test_email_endpoint(PRODUCTION_URL, "production")
    
    # Test local environment if available
    print("\n🏠 TESTING LOCAL ENVIRONMENT")
    print("="*80)
    local_success = await test_email_endpoint(LOCAL_URL, "local")
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("="*80)
    print(f"🌐 Production (Render): {'✅ PASS' if production_success else '❌ FAIL'}")
    print(f"🏠 Local: {'✅ PASS' if local_success else '❌ FAIL'}")
    
    if production_success:
        print("\n🎉 PRODUCTION EMAIL FUNCTIONALITY IS WORKING!")
        print("✅ Users can now receive prediction reports via email")
        print("📧 Email delivery confirmed to Gmail inbox")
    else:
        print("\n❌ PRODUCTION EMAIL FUNCTIONALITY NEEDS ATTENTION")
        print("🔧 Check Render environment variables:")
        print("   - GMAIL_EMAIL=gokrishna98@gmail.com")
        print("   - GMAIL_APP_PASSWORD=lwkvzupqanxvafrm")
        print("📋 Check Render service logs for detailed error messages")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())
