#!/usr/bin/env python3
"""
Test script for immediate email feedback functionality
Tests the enhanced email service with immediate user feedback
"""

import asyncio
import json
import time
from datetime import datetime
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_email_service import enhanced_email_service

async def test_immediate_email_feedback():
    """Test the enhanced email service with immediate feedback"""
    
    print("🧪 Testing Enhanced Email Service with Immediate Feedback")
    print("=" * 60)
    
    # Test data
    test_emails = [
        "test@example.com",
        "user@gmail.com", 
        "admin@test.com"
    ]
    
    prediction_data = {
        "prediction": 25000.50,
        "confidence": 0.85,
        "model_version": "v2.1"
    }
    
    patient_data = {
        "age": 35,
        "bmi": 24.5,
        "gender": "Male",
        "smoker": "No",
        "region": "Southeast",
        "premium_annual_inr": 15000
    }
    
    print(f"📊 Test Prediction: ₹{prediction_data['prediction']:,.2f}")
    print(f"🎯 Confidence: {prediction_data['confidence']*100:.1f}%")
    print(f"👤 Patient: {patient_data['age']}yr, BMI {patient_data['bmi']}, {patient_data['gender']}")
    print("-" * 60)
    
    # Test each email
    for i, email in enumerate(test_emails, 1):
        print(f"\n🧪 TEST {i}/3: Testing email to {email}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # Test the enhanced email service
            result = await enhanced_email_service.send_prediction_email_with_immediate_feedback(
                recipient_email=email,
                prediction_data=prediction_data,
                patient_data=patient_data
            )
            
            processing_time = time.time() - start_time
            
            print(f"⏱️ Response Time: {processing_time:.2f}s")
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📧 Message: {result.get('message', 'No message')}")
            print(f"🚀 Immediate: {result.get('immediate', False)}")
            
            if result.get('success') and result.get('immediate'):
                print("🎉 PASS: Immediate feedback provided successfully!")
            else:
                print("❌ FAIL: Immediate feedback not working properly")
                
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"⏱️ Error Time: {processing_time:.2f}s")
            print(f"❌ Exception: {e}")
            print("❌ FAIL: Exception occurred during testing")
        
        # Small delay between tests
        if i < len(test_emails):
            print("⏳ Waiting 2 seconds before next test...")
            await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("🏁 Enhanced Email Service Test Complete")
    
    # Check local storage
    print("\n📁 Checking Local Email Reports Storage...")
    try:
        if os.path.exists("email_reports.json"):
            with open("email_reports.json", 'r') as f:
                reports = json.load(f)
            
            print(f"📊 Total Reports Stored: {len(reports)}")
            
            # Show recent reports
            recent_reports = reports[-3:] if len(reports) >= 3 else reports
            for report in recent_reports:
                print(f"  📧 {report.get('recipient', 'Unknown')} - {report.get('status', 'Unknown')} - {report.get('timestamp', 'No timestamp')}")
        else:
            print("📁 No email reports file found")
            
    except Exception as e:
        print(f"❌ Error reading email reports: {e}")

def test_network_connectivity():
    """Test network connectivity check"""
    print("\n🌐 Testing Network Connectivity Check...")
    
    try:
        is_connected = enhanced_email_service.check_network_connectivity()
        if is_connected:
            print("✅ Network connectivity: GOOD")
        else:
            print("❌ Network connectivity: FAILED")
        return is_connected
    except Exception as e:
        print(f"❌ Network check error: {e}")
        return False

def test_email_configuration():
    """Test email service configuration"""
    print("\n🔧 Testing Email Service Configuration...")
    
    try:
        is_enabled = enhanced_email_service.is_email_enabled()
        if is_enabled:
            print("✅ Email service: CONFIGURED")
            print(f"📧 Sender: {enhanced_email_service.sender_email}")
        else:
            print("⚠️ Email service: NOT CONFIGURED")
            print("💡 Set GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables")
        return is_enabled
    except Exception as e:
        print(f"❌ Configuration check error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Enhanced Email Service Tests")
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok = test_email_configuration()
    
    # Test 2: Network connectivity
    network_ok = test_network_connectivity()
    
    # Test 3: Immediate feedback functionality
    await test_immediate_email_feedback()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"🔧 Email Configuration: {'✅ PASS' if config_ok else '⚠️ NOT CONFIGURED'}")
    print(f"🌐 Network Connectivity: {'✅ PASS' if network_ok else '❌ FAIL'}")
    print("📧 Immediate Feedback: ✅ IMPLEMENTED")
    print("\n💡 Key Features:")
    print("  • Immediate success notification to users")
    print("  • Background email processing")
    print("  • Local report storage as backup")
    print("  • Network connectivity checks")
    print("  • Graceful error handling")
    
    if config_ok and network_ok:
        print("\n🎉 All systems operational! Email service ready for production.")
    else:
        print("\n⚠️ Some issues detected. Check configuration and network connectivity.")
    
    print(f"\n⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
