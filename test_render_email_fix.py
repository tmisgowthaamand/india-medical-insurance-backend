#!/usr/bin/env python3
"""
Test Render Email Fix - MediCare+ Platform
Tests the new render-optimized email service to resolve Gmail connection issues
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_render_email_fix():
    """Test the render email fix comprehensively"""
    print("🧪 TESTING RENDER EMAIL FIX")
    print("="*70)
    
    # Import the new render email service
    from render_email_service import render_email_service
    
    # Test 1: Check environment variables
    print("\n🔍 TEST 1: Environment Variables")
    print("-" * 40)
    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"GMAIL_EMAIL: {'✅ SET' if gmail_email else '❌ NOT SET'}")
    if gmail_email:
        print(f"   Value: {gmail_email}")
    
    print(f"GMAIL_APP_PASSWORD: {'✅ SET' if gmail_password else '❌ NOT SET'}")
    if gmail_password:
        print(f"   Length: {len(gmail_password)} characters")
    
    # Test 2: Gmail connection
    print("\n🔗 TEST 2: Gmail Connection")
    print("-" * 40)
    connection_result = render_email_service.test_gmail_connection()
    print(f"Connection Test: {'✅ PASS' if connection_result['success'] else '❌ FAIL'}")
    print(f"Message: {connection_result['message']}")
    
    if not connection_result['success']:
        print(f"Error Type: {connection_result['error']}")
        if 'details' in connection_result:
            print(f"Details: {connection_result['details']}")
        if 'fix_instructions' in connection_result:
            print("Fix Instructions:")
            for instruction in connection_result['fix_instructions']:
                print(f"  {instruction}")
        
        print("\n❌ EMAIL SERVICE NOT CONFIGURED PROPERLY")
        print("💡 To fix this on Render:")
        print("1. Go to your Render dashboard")
        print("2. Select your backend service")
        print("3. Go to Environment tab")
        print("4. Add these environment variables:")
        print("   - GMAIL_EMAIL: gokrishna98@gmail.com")
        print("   - GMAIL_APP_PASSWORD: lwkvzupqanxvafrm")
        print("5. Deploy the service")
        return
    
    # Test 3: Send test email
    print("\n📧 TEST 3: Send Test Email")
    print("-" * 40)
    test_email = "perivihari8@gmail.com"
    test_prediction = {
        "prediction": 19777.48,
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
    
    print(f"Sending test email to: {test_email}")
    result = await render_email_service.send_prediction_email(
        recipient_email=test_email,
        prediction_data=test_prediction,
        patient_data=test_patient_data
    )
    
    print(f"Email Test: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"Delivery Status: {result.get('delivery_status', 'unknown')}")
    else:
        if 'error_type' in result:
            print(f"Error Type: {result['error_type']}")
        if 'details' in result:
            print(f"Details: {result['details']}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    if connection_result['success'] and result['success']:
        print("✅ ALL TESTS PASSED")
        print("🎉 Email functionality is working correctly!")
        print("📧 Users can now receive prediction reports via email")
    elif connection_result['success'] and not result['success']:
        print("⚠️ CONNECTION OK, EMAIL SENDING FAILED")
        print("🔧 Gmail connection works but email delivery failed")
        print("💡 Check recipient email address and try again")
    else:
        print("❌ EMAIL SERVICE NOT CONFIGURED")
        print("🔧 Gmail credentials need to be set in environment variables")
        print("📋 Follow the fix instructions above")

if __name__ == "__main__":
    asyncio.run(test_render_email_fix())
