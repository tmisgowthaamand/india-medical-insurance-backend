#!/usr/bin/env python3
"""
Enhanced Email Fix Test Script
Tests the improved email functionality with better timeout handling and error reporting
"""

import asyncio
import requests
import time
import json
from datetime import datetime

def test_enhanced_email_functionality():
    """Test the enhanced email functionality end-to-end"""
    print("🧪 TESTING ENHANCED EMAIL FUNCTIONALITY")
    print("="*80)
    
    # Test configuration
    backend_url = "http://localhost:8001"  # Local backend
    render_url = "https://srv-d3b668ogjchc73f9ece0-latest.onrender.com"  # Render backend
    
    test_emails = [
        "gowthaamankrishna1998@gmail.com",  # User's email
        "test@example.com"  # Test email
    ]
    
    test_prediction = {
        "prediction": 28500.75,
        "confidence": 0.89
    }
    
    test_patient_data = {
        "age": 32,
        "bmi": 26.8,
        "gender": "Male",
        "smoker": "No",
        "region": "South",
        "premium_annual_inr": 25000,
        "report_generated": datetime.now().isoformat()
    }
    
    # Test both local and Render backends
    backends = [
        ("Local Backend", backend_url),
        ("Render Backend", render_url)
    ]
    
    for backend_name, base_url in backends:
        print(f"\n🏗️ TESTING {backend_name}")
        print("-" * 60)
        
        # Test 1: Health check
        print("1. Testing health endpoint...")
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}/health", timeout=30)
            health_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Health check passed ({health_time:.2f}s)")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                continue
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            continue
        
        # Test 2: Email functionality
        for email in test_emails:
            print(f"\n2. Testing email to: {email}")
            
            email_data = {
                "email": email,
                "prediction": test_prediction,
                "patient_data": test_patient_data
            }
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{base_url}/send-prediction-email",
                    json=email_data,
                    timeout=180,  # 3 minutes timeout
                    headers={"Content-Type": "application/json"}
                )
                email_time = time.time() - start_time
                
                print(f"   ⏱️ Response time: {email_time:.2f}s")
                print(f"   📊 Status code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    success = result.get("success", False)
                    message = result.get("message", "No message")
                    
                    print(f"   📧 Success: {success}")
                    print(f"   💬 Message: {message}")
                    
                    if success:
                        print(f"   ✅ Email test PASSED for {email}")
                        if email == "gowthaamankrishna1998@gmail.com":
                            print(f"   📬 Check Gmail inbox for: {email}")
                    else:
                        print(f"   ⚠️ Email test FAILED for {email}")
                        print(f"   🔍 Reason: {message}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"   🔍 Error: {error_detail}")
                    except:
                        print(f"   🔍 Raw response: {response.text}")
                        
            except requests.exceptions.Timeout:
                email_time = time.time() - start_time
                print(f"   ⏰ Email request timed out after {email_time:.2f}s")
            except Exception as e:
                email_time = time.time() - start_time
                print(f"   ❌ Email test error after {email_time:.2f}s: {e}")
    
    print(f"\n{'='*80}")
    print("🏁 EMAIL FUNCTIONALITY TEST COMPLETED")
    print("="*80)
    print("\n📋 SUMMARY:")
    print("✅ If emails were sent successfully, check Gmail inbox")
    print("❌ If errors occurred, check the error messages above")
    print("⏱️ Note the response times for performance analysis")
    print("\n🔧 TROUBLESHOOTING:")
    print("1. Ensure backend is running (local: uvicorn app:app --host 0.0.0.0 --port 8001)")
    print("2. Check Gmail credentials in environment variables")
    print("3. Verify internet connection for Gmail SMTP")
    print("4. Check Render deployment status if testing production")

def test_bulletproof_service_directly():
    """Test the bulletproof email service directly"""
    print("\n🛡️ TESTING BULLETPROOF EMAIL SERVICE DIRECTLY")
    print("="*80)
    
    try:
        from bulletproof_email_service import bulletproof_email_service
        
        # Test connection
        print("1. Testing Gmail connection...")
        connection_result = bulletproof_email_service.test_gmail_connection()
        
        if connection_result["success"]:
            print("   ✅ Gmail connection successful")
            
            # Test email sending
            print("\n2. Testing email sending...")
            test_email = "gowthaamankrishna1998@gmail.com"
            test_prediction = {"prediction": 25000, "confidence": 0.88}
            test_patient_data = {
                "age": 28, "bmi": 24.5, "gender": "Male", "smoker": "No", 
                "region": "South", "premium_annual_inr": 22000
            }
            
            async def send_test():
                result = await bulletproof_email_service.send_prediction_email(
                    recipient_email=test_email,
                    prediction_data=test_prediction,
                    patient_data=test_patient_data
                )
                return result
            
            result = asyncio.run(send_test())
            
            if result["success"]:
                print(f"   ✅ Email sent successfully to {test_email}")
                print(f"   ⏱️ Processing time: {result.get('processing_time', 0):.2f}s")
            else:
                print(f"   ❌ Email sending failed: {result['message']}")
        else:
            print(f"   ❌ Gmail connection failed: {connection_result['message']}")
            if 'fix_instructions' in connection_result:
                print("   🔧 Fix instructions:")
                for instruction in connection_result['fix_instructions']:
                    print(f"      • {instruction}")
                    
    except Exception as e:
        print(f"❌ Direct service test error: {e}")

if __name__ == "__main__":
    print("🚀 STARTING ENHANCED EMAIL FUNCTIONALITY TESTS")
    print("="*80)
    
    # Test 1: API endpoints
    test_enhanced_email_functionality()
    
    # Test 2: Direct service
    test_bulletproof_service_directly()
    
    print(f"\n🎯 TESTING COMPLETED AT: {datetime.now()}")
