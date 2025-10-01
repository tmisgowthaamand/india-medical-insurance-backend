#!/usr/bin/env python3
"""
Comprehensive Email Test for MediCare+ Platform
Tests email functionality with existing and new email addresses
"""

import os
import sys
import asyncio
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_endpoint(base_url, email, test_name):
    """Test the email endpoint with given email"""
    
    print(f"\n🧪 {test_name}")
    print("=" * 50)
    
    # Test data
    test_data = {
        "email": email,
        "prediction": {
            "prediction": 25000.0,
            "confidence": 0.85
        },
        "patient_data": {
            "age": 35,
            "bmi": 23.0,
            "gender": "Male",
            "smoker": "No",
            "region": "East",
            "premium_annual_inr": 30000
        }
    }
    
    try:
        print(f"📧 Testing email: {email}")
        print(f"🌐 Endpoint: {base_url}/send-prediction-email")
        
        response = requests.post(
            f"{base_url}/send-prediction-email",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📝 Message: {result.get('message', 'No message')}")
            return result.get('success', False)
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error Message: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"📝 Error Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🏥 MediCare+ Email Functionality Test")
    print("=" * 60)
    
    # Test both localhost and Render
    test_urls = [
        ("http://localhost:8001", "Localhost Backend"),
        ("https://srv-d3b668ogjchc73f9ece0.onrender.com", "Render Backend")
    ]
    
    # Test emails
    test_emails = [
        ("perivihk@gmail.com", "Existing User Email"),
        ("gokrishna98@gmail.com", "Test Email 1"),
        ("test.medicare@gmail.com", "Test Email 2")
    ]
    
    results = []
    
    for base_url, url_name in test_urls:
        print(f"\n🌐 Testing {url_name}: {base_url}")
        print("=" * 60)
        
        # Test health endpoint first
        try:
            health_response = requests.get(f"{base_url}/health", timeout=10)
            if health_response.status_code == 200:
                print(f"✅ {url_name} is accessible")
            else:
                print(f"⚠️ {url_name} health check failed: {health_response.status_code}")
                continue
        except Exception as e:
            print(f"❌ {url_name} is not accessible: {e}")
            continue
        
        # Test email functionality
        for email, email_desc in test_emails:
            success = test_email_endpoint(base_url, email, f"{email_desc} on {url_name}")
            results.append({
                "url": url_name,
                "email": email,
                "success": success
            })
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['url']} - {result['email']}")
    
    if successful_tests == total_tests:
        print("\n🎉 All email tests passed!")
    else:
        print("\n⚠️ Some email tests failed - check configuration")

if __name__ == "__main__":
    main()
