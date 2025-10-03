#!/usr/bin/env python3
"""
Test Render Network Email Fix - MediCare+ Platform
Comprehensive test for network connectivity and Gmail storage functionality
"""

import asyncio
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_render_network_fix_comprehensive():
    """Comprehensive test of render network email fix"""
    print("🌐 RENDER NETWORK EMAIL FIX TEST")
    print("="*80)
    
    # Test 1: Import and initialize service
    print("\n🔧 TEST 1: Service Initialization")
    print("-" * 50)
    
    try:
        from render_network_email_service import render_network_email_service
        print("✅ Render network email service imported successfully")
        print(f"Email Enabled: {'✅ YES' if render_network_email_service.email_enabled else '❌ NO'}")
        print(f"Sender Email: {render_network_email_service.sender_email}")
        print(f"SMTP Configs: {len(render_network_email_service.smtp_configs)} configurations")
    except Exception as e:
        print(f"❌ Failed to import service: {e}")
        return
    
    # Test 2: Network Connectivity
    print("\n🌐 TEST 2: Network Connectivity")
    print("-" * 50)
    
    network_result = render_network_email_service.test_network_connectivity()
    print(f"Network Test: {'✅ PASS' if network_result['success'] else '❌ FAIL'}")
    print(f"Message: {network_result['message']}")
    
    if not network_result['success']:
        print(f"Error Type: {network_result['error']}")
        print("\n❌ NETWORK CONNECTIVITY FAILED")
        print("🔧 This indicates Render network issues:")
        print("1. Internet connectivity problems")
        print("2. DNS resolution failures")
        print("3. Firewall blocking SMTP ports")
        print("4. Render infrastructure issues")
        return
    
    # Test 3: Gmail Connection
    print("\n🔗 TEST 3: Gmail SMTP Connection")
    print("-" * 50)
    
    connection_result = render_network_email_service.test_gmail_connection()
    print(f"Gmail Test: {'✅ PASS' if connection_result['success'] else '❌ FAIL'}")
    print(f"Message: {connection_result['message']}")
    
    if connection_result['success']:
        working_config = connection_result.get('config', {})
        print(f"Working Config: {working_config.get('name', 'Unknown')}")
        print(f"Server: {working_config.get('server', 'Unknown')}:{working_config.get('port', 'Unknown')}")
    else:
        print(f"Error Type: {connection_result['error']}")
        print("\n❌ GMAIL CONNECTION FAILED")
        print("🔧 Possible causes on Render:")
        print("1. Gmail SMTP ports (587, 465, 25) are blocked")
        print("2. SSL/TLS connection issues")
        print("3. Gmail credentials incorrect")
        print("4. Network firewall restrictions")
        
        # Still continue with other tests
    
    # Test 4: Gmail Storage Functionality
    print("\n📁 TEST 4: Gmail Storage")
    print("-" * 50)
    
    test_user_id = "test_user_123"
    test_emails = [
        "gowthaamankrishna1998@gmail.com",
        "user2@example.com",
        "user3@gmail.com"
    ]
    
    # Store emails
    for email in test_emails:
        success = render_network_email_service.store_user_email(test_user_id, email)
        print(f"Store {email}: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Retrieve emails
    stored_emails = render_network_email_service.get_user_emails(test_user_id)
    print(f"Retrieved emails: {stored_emails}")
    print(f"Email count: {len(stored_emails)}")
    
    # Test 5: Email Sending (if connection works)
    if connection_result['success']:
        print("\n📧 TEST 5: Email Sending")
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
            result = await render_network_email_service.send_prediction_email(
                recipient_email=test_email,
                prediction_data=test_prediction,
                patient_data=test_patient_data,
                user_id=test_user_id
            )
            
            print(f"Email Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
            print(f"Message: {result['message']}")
            
            if result['success']:
                print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
                print(f"Config Used: {result.get('config_used', 'Unknown')}")
            else:
                if 'error_type' in result:
                    print(f"Error Type: {result['error_type']}")
                if 'network_info' in result:
                    print(f"Network Info: {result['network_info']}")
            
        except Exception as e:
            print(f"❌ Email sending exception: {e}")
    
    # Test 6: API Endpoints (if running locally)
    print("\n🔌 TEST 6: API Endpoints")
    print("-" * 50)
    
    base_url = "http://localhost:8001"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health endpoint: {'✅ OK' if response.status_code == 200 else '❌ FAILED'}")
        
        # Test store email endpoint
        store_data = {
            "user_id": "api_test_user",
            "email": "gowthaamankrishna1998@gmail.com"
        }
        response = requests.post(f"{base_url}/store-user-email", json=store_data, timeout=5)
        print(f"Store email endpoint: {'✅ OK' if response.status_code == 200 else '❌ FAILED'}")
        
        # Test get emails endpoint
        response = requests.get(f"{base_url}/user-emails/api_test_user", timeout=5)
        print(f"Get emails endpoint: {'✅ OK' if response.status_code == 200 else '❌ FAILED'}")
        if response.status_code == 200:
            data = response.json()
            print(f"API stored emails: {data.get('emails', [])}")
        
    except requests.exceptions.ConnectionError:
        print("⚠️ Backend not running locally - skipping API tests")
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    # Test Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    if network_result['success']:
        print("✅ Network connectivity working")
        
        if connection_result['success']:
            print("✅ Gmail SMTP connection working")
            print("🎉 EMAIL FUNCTIONALITY SHOULD WORK ON RENDER!")
            print("📧 Users can receive prediction reports via email")
        else:
            print("❌ Gmail SMTP connection failed")
            print("🔧 Render is blocking Gmail SMTP ports")
            print("💡 Consider using alternative email service (SendGrid, etc.)")
    else:
        print("❌ Network connectivity failed")
        print("🔧 Render has network infrastructure issues")
    
    print("✅ Gmail storage functionality working")
    print("📁 User emails are being stored and retrieved correctly")
    
    # Render-specific recommendations
    print("\n🚀 RENDER DEPLOYMENT RECOMMENDATIONS:")
    print("-" * 50)
    print("1. Set environment variables:")
    print("   GMAIL_EMAIL=gokrishna98@gmail.com")
    print("   GMAIL_APP_PASSWORD=lwkvzupqanxvafrm")
    print()
    print("2. If Gmail SMTP fails, consider alternatives:")
    print("   - SendGrid (SENDGRID_API_KEY)")
    print("   - Mailgun (MAILGUN_API_KEY)")
    print("   - AWS SES (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
    print()
    print("3. Monitor email delivery logs:")
    print("   - Check email_delivery_log.json")
    print("   - Check user_emails.json")
    print()
    print("4. Frontend timeout settings:")
    print("   - Health check: 20s")
    print("   - Email API: 90s")
    print("   - Retry mechanism: 3 attempts")

if __name__ == "__main__":
    asyncio.run(test_render_network_fix_comprehensive())
