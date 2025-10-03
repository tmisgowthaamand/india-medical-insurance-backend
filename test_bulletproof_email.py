#!/usr/bin/env python3
"""
Test Bulletproof Email Service - MediCare+ Platform
Comprehensive testing for Gmail connection issues on Render
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_bulletproof_email_comprehensive():
    """Comprehensive test of bulletproof email service"""
    print("🛡️ BULLETPROOF EMAIL SERVICE TEST")
    print("="*80)
    
    # Import the bulletproof service
    try:
        from bulletproof_email_service import bulletproof_email_service
        print("✅ Bulletproof email service imported successfully")
    except Exception as e:
        print(f"❌ Failed to import bulletproof email service: {e}")
        return
    
    # Test 1: Environment Check
    print("\n🔍 TEST 1: Environment Variables")
    print("-" * 50)
    
    env_vars = [
        "GMAIL_EMAIL", "EMAIL_USER", "SMTP_EMAIL", "SENDER_EMAIL",
        "GMAIL_APP_PASSWORD", "EMAIL_PASSWORD", "SMTP_PASSWORD", "APP_PASSWORD"
    ]
    
    found_vars = {}
    for var in env_vars:
        value = os.getenv(var)
        if value:
            found_vars[var] = value
            print(f"✅ {var}: {value}")
    
    if not found_vars:
        print("❌ No email environment variables found")
        print("💡 The service will use fallback credentials")
    
    # Test 2: Service Initialization
    print("\n🚀 TEST 2: Service Initialization")
    print("-" * 50)
    
    print(f"Email Enabled: {'✅ YES' if bulletproof_email_service.email_enabled else '❌ NO'}")
    print(f"Sender Email: {bulletproof_email_service.sender_email}")
    print(f"Password Length: {len(bulletproof_email_service.sender_password)} chars")
    
    # Test 3: Gmail Connection Test
    print("\n🔗 TEST 3: Gmail Connection")
    print("-" * 50)
    
    connection_result = bulletproof_email_service.test_gmail_connection()
    
    print(f"Connection Result: {'✅ SUCCESS' if connection_result['success'] else '❌ FAILED'}")
    print(f"Message: {connection_result['message']}")
    
    if not connection_result['success']:
        print(f"Error Type: {connection_result.get('error', 'Unknown')}")
        if 'details' in connection_result:
            print(f"Details: {connection_result['details']}")
        if 'fix_instructions' in connection_result:
            print("Fix Instructions:")
            for i, instruction in enumerate(connection_result['fix_instructions'], 1):
                print(f"  {i}. {instruction}")
        
        print("\n❌ CONNECTION TEST FAILED")
        print("🔧 TROUBLESHOOTING STEPS:")
        print("1. Check if Gmail credentials are correct")
        print("2. Verify 2FA is enabled on Gmail account")
        print("3. Generate new Gmail App Password")
        print("4. Set environment variables in Render:")
        print("   GMAIL_EMAIL=gokrishna98@gmail.com")
        print("   GMAIL_APP_PASSWORD=lwkvzupqanxvafrm")
        return
    
    # Test 4: Email Sending
    print("\n📧 TEST 4: Email Sending")
    print("-" * 50)
    
    test_email = "gowthaamankrishna1998@gmail.com"
    test_prediction = {
        "prediction": 25000,
        "confidence": 0.88
    }
    test_patient_data = {
        "age": 28,
        "bmi": 24.5,
        "gender": "Male",
        "smoker": "No",
        "region": "South",
        "premium_annual_inr": 22000
    }
    
    print(f"Sending test email to: {test_email}")
    
    try:
        result = await bulletproof_email_service.send_prediction_email(
            recipient_email=test_email,
            prediction_data=test_prediction,
            patient_data=test_patient_data
        )
        
        print(f"Email Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        print(f"Message: {result['message']}")
        
        if result['success']:
            print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
            print(f"Delivery Status: {result.get('delivery_status', 'unknown')}")
            print(f"Attempts: {result.get('attempt', 'unknown')}")
        else:
            if 'error_type' in result:
                print(f"Error Type: {result['error_type']}")
            if 'details' in result:
                print(f"Details: {result['details']}")
            if 'last_error' in result:
                print(f"Last Error: {result['last_error']}")
        
    except Exception as e:
        print(f"❌ Email sending exception: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    # Test Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    if connection_result['success']:
        print("✅ Gmail connection working")
        if 'result' in locals() and result['success']:
            print("✅ Email sending working")
            print("🎉 ALL TESTS PASSED - Email functionality is working!")
        else:
            print("❌ Email sending failed")
            print("🔧 Gmail connects but email delivery fails")
    else:
        print("❌ Gmail connection failed")
        print("🔧 Need to fix Gmail credentials first")
    
    # Platform Info
    print(f"\n🖥️ Platform: {sys.platform}")
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Working Dir: {os.getcwd()}")
    
    # Render Detection
    if 'RENDER' in os.environ:
        print("🚀 Running on Render")
        print("💡 Make sure environment variables are set in Render dashboard")
    else:
        print("🏠 Running locally")
        print("💡 Check .env file for credentials")

if __name__ == "__main__":
    asyncio.run(test_bulletproof_email_comprehensive())
