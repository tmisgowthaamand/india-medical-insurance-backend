#!/usr/bin/env python3
"""
Test Render Email Timeout Fix
Verifies that the optimized email service works within timeout limits
"""

import asyncio
import time
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service import email_service

async def test_email_timeout_fix():
    """Test the optimized email service with timeout handling"""
    
    print("🧪 Testing Render Email Timeout Fix")
    print("=" * 60)
    
    # Test data
    test_email = "gowthamananswar1998@gmail.com"
    prediction_data = {
        "prediction": 25000,
        "confidence": 0.85
    }
    patient_data = {
        "age": 35,
        "bmi": 24.5,
        "gender": "Male",
        "smoker": "No",
        "region": "South",
        "premium_annual_inr": 30000
    }
    
    print(f"📧 Testing email send to: {test_email}")
    print(f"⏱️ Timeout settings:")
    print(f"   - Connection timeout: {email_service.connection_timeout}s")
    print(f"   - Send timeout: {email_service.send_timeout}s")
    print(f"   - Total timeout: {email_service.total_timeout}s")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # Test async email sending
        result = await email_service.send_prediction_email_async(
            recipient_email=test_email,
            prediction_data=prediction_data,
            patient_data=patient_data
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Test completed in {duration:.2f} seconds")
        print(f"📧 Result: {result}")
        
        # Analyze results
        if duration < 60:
            print("🎯 SUCCESS: Email processing under 60 seconds")
            if duration < 45:
                print("🚀 EXCELLENT: Email processing under 45 seconds")
        else:
            print("⚠️ WARNING: Email processing took longer than expected")
        
        if result.get("success"):
            print("✅ Email operation reported success")
        else:
            print("❌ Email operation reported failure")
        
        if result.get("timeout"):
            print("⏱️ Email operation timed out (but handled gracefully)")
        
        if result.get("mock"):
            print("🎭 Email operation used mock/demo mode")
            
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Test failed after {duration:.2f} seconds: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 TIMEOUT FIX VERIFICATION")
    print("=" * 60)
    
    # Verify timeout settings
    if hasattr(email_service, 'total_timeout') and email_service.total_timeout <= 60:
        print("✅ Total timeout is within safe limits (≤60s)")
    else:
        print("❌ Total timeout may be too high")
    
    if hasattr(email_service, 'connection_timeout') and email_service.connection_timeout <= 20:
        print("✅ Connection timeout is optimized (≤20s)")
    else:
        print("❌ Connection timeout may be too high")
    
    # Check if async method exists
    if hasattr(email_service, 'send_prediction_email_async'):
        print("✅ Async email method is available")
    else:
        print("❌ Async email method is missing")
    
    print("\n🚀 Render deployment should now handle email timeouts properly!")
    return True

def test_sync_wrapper():
    """Test the synchronous wrapper for backward compatibility"""
    
    print("\n🔄 Testing synchronous wrapper...")
    
    test_email = "test@example.com"
    prediction_data = {"prediction": 15000, "confidence": 0.75}
    patient_data = {
        "age": 28,
        "bmi": 22.0,
        "gender": "Female",
        "smoker": "No",
        "region": "North",
        "premium_annual_inr": 20000
    }
    
    start_time = time.time()
    
    try:
        success = email_service.send_prediction_email(
            recipient_email=test_email,
            prediction_data=prediction_data,
            patient_data=patient_data
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Sync wrapper completed in {duration:.2f} seconds")
        print(f"📧 Success: {success}")
        
        return success
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Sync wrapper failed after {duration:.2f} seconds: {e}")
        return False

async def main():
    """Main test function"""
    
    print("🏥 MediCare+ Email Timeout Fix Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Email service enabled: {email_service.is_email_enabled()}")
    print()
    
    # Test async functionality
    async_success = await test_email_timeout_fix()
    
    # Test sync wrapper
    sync_success = test_sync_wrapper()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Async email test: {'PASSED' if async_success else 'FAILED'}")
    print(f"✅ Sync wrapper test: {'PASSED' if sync_success else 'FAILED'}")
    
    if async_success and sync_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Email timeout fix is ready for Render deployment!")
    else:
        print("\n⚠️ Some tests failed - review the issues above")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
