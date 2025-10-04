#!/usr/bin/env python3
"""
Render Email Deployment Test Script
Tests email functionality specifically for Render deployment with enhanced timeout handling
"""

import asyncio
import requests
import time
import json
from datetime import datetime

def test_render_email_deployment():
    """Test email functionality on Render deployment with proper timeout handling"""
    print("🚀 TESTING RENDER EMAIL DEPLOYMENT")
    print("="*80)
    
    # Render backend URL
    render_url = "https://srv-d3b668ogjchc73f9ece0-latest.onrender.com"
    
    test_emails = [
        "gowthaamankrishna1998@gmail.com",  # User's email
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
    
    print(f"🎯 Testing Render Backend: {render_url}")
    print("-" * 60)
    
    # Test 1: Health check with extended timeout
    print("1. Testing health endpoint (extended timeout for cold start)...")
    try:
        start_time = time.time()
        response = requests.get(f"{render_url}/health", timeout=60)  # 60 second timeout
        health_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Health check passed ({health_time:.2f}s)")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except requests.exceptions.Timeout:
        health_time = time.time() - start_time
        print(f"   ⏰ Health check timed out after {health_time:.2f}s")
        print("   ⚠️ Service may be sleeping - continuing with email test...")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        print("   ⚠️ Continuing with email test anyway...")
    
    # Test 2: Email functionality with extended timeout
    for email in test_emails:
        print(f"\n2. Testing email to: {email}")
        
        email_data = {
            "email": email,
            "prediction": test_prediction,
            "patient_data": test_patient_data
        }
        
        try:
            start_time = time.time()
            print("   📧 Sending email request (this may take 2-4 minutes for cold start)...")
            
            response = requests.post(
                f"{render_url}/send-prediction-email",
                json=email_data,
                timeout=300,  # 5 minutes timeout for cold start
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
                    print(f"   ✅ EMAIL TEST PASSED for {email}")
                    print(f"   📬 Check Gmail inbox for: {email}")
                    print(f"   🎉 Email delivered in {email_time:.2f}s")
                else:
                    print(f"   ⚠️ EMAIL TEST FAILED for {email}")
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
            print(f"   💡 This usually means the service is cold starting")
            print(f"   🔄 Try again in a few minutes when service is warm")
        except Exception as e:
            email_time = time.time() - start_time
            print(f"   ❌ Email test error after {email_time:.2f}s: {e}")
    
    print(f"\n{'='*80}")
    print("🏁 RENDER EMAIL DEPLOYMENT TEST COMPLETED")
    print("="*80)
    print("\n📋 SUMMARY:")
    print("✅ If emails were sent successfully, check Gmail inbox")
    print("❌ If timeout errors occurred, the service may be cold starting")
    print("⏱️ Cold starts can take 2-4 minutes on Render free tier")
    print("\n🔧 TROUBLESHOOTING:")
    print("1. Wait 2-3 minutes and try again (service warm-up)")
    print("2. Check Render service logs for detailed error messages")
    print("3. Verify environment variables are set correctly")
    print("4. Ensure Gmail credentials are valid")

def test_render_service_warmup():
    """Test to warm up the Render service"""
    print("\n🔥 WARMING UP RENDER SERVICE")
    print("="*50)
    
    render_url = "https://srv-d3b668ogjchc73f9ece0-latest.onrender.com"
    
    # Multiple quick requests to warm up the service
    for i in range(3):
        try:
            print(f"   🏥 Warmup request {i+1}/3...")
            start_time = time.time()
            
            response = requests.get(f"{render_url}/health", timeout=30)
            warmup_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Warmup {i+1} successful ({warmup_time:.2f}s)")
                if warmup_time < 5:
                    print("   🔥 Service is now warm!")
                    break
            else:
                print(f"   ⚠️ Warmup {i+1} returned {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Warmup {i+1} failed: {e}")
        
        if i < 2:  # Don't wait after last attempt
            print("   ⏳ Waiting 10 seconds before next attempt...")
            time.sleep(10)

if __name__ == "__main__":
    print("🚀 STARTING RENDER EMAIL DEPLOYMENT TESTS")
    print("="*80)
    
    # Step 1: Warm up the service
    test_render_service_warmup()
    
    # Step 2: Test email functionality
    test_render_email_deployment()
    
    print(f"\n🎯 TESTING COMPLETED AT: {datetime.now()}")
    print("\n💡 TIP: If you got timeout errors, try running this script again.")
    print("The service should be warmed up now and respond faster.")
