#!/usr/bin/env python3
"""
Test Fix for Existing Email Issue
Specifically tests the perivihk@gmail.com email that was causing issues
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_existing_email_fix():
    """Test the specific email that was causing issues"""
    
    print("🧪 Testing Fix for Existing Email Issue")
    print("=" * 60)
    
    # The email that was causing the issue
    test_email = "perivihk@gmail.com"
    
    # Test data matching the original request
    test_data = {
        "email": test_email,
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
    
    # Test localhost backend
    localhost_url = "http://localhost:8001"
    
    print(f"📧 Testing existing email: {test_email}")
    print(f"🌐 Backend: {localhost_url}")
    print(f"📊 Test Data: {json.dumps(test_data, indent=2)}")
    
    try:
        print("\n🚀 Sending request...")
        response = requests.post(
            f"{localhost_url}/send-prediction-email",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📝 Message: {result.get('message', 'No message')}")
            
            if result.get('success'):
                print("\n🎉 EMAIL FIX SUCCESSFUL!")
                print("✅ Existing email can now receive prediction reports")
                print("📬 Check the inbox for the email")
                return True
            else:
                print("\n❌ Email sending failed")
                return False
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"📝 Error Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

def test_multiple_existing_emails():
    """Test multiple emails that might exist in the database"""
    
    print("\n🧪 Testing Multiple Existing Emails")
    print("=" * 60)
    
    # Test emails that might exist in the database
    test_emails = [
        "perivihk@gmail.com",
        "gokrishna98@gmail.com",
        "admin@medicare.com",
        "test@example.com"
    ]
    
    results = []
    localhost_url = "http://localhost:8001"
    
    for email in test_emails:
        print(f"\n📧 Testing: {email}")
        
        test_data = {
            "email": email,
            "prediction": {
                "prediction": 22000.0,
                "confidence": 0.78
            },
            "patient_data": {
                "age": 30,
                "bmi": 22.5,
                "gender": "Female",
                "smoker": "No",
                "region": "West",
                "premium_annual_inr": 25000
            }
        }
        
        try:
            response = requests.post(
                f"{localhost_url}/send-prediction-email",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                message = result.get('message', 'No message')
                
                print(f"✅ Status: {success}")
                print(f"📝 Message: {message}")
                
                results.append({
                    "email": email,
                    "success": success,
                    "message": message
                })
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                results.append({
                    "email": email,
                    "success": False,
                    "message": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "email": email,
                "success": False,
                "message": str(e)
            })
    
    # Summary
    print("\n📊 MULTIPLE EMAIL TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"Total Emails Tested: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {(successful/total*100):.1f}%" if total > 0 else "No tests")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['email']}: {result['message']}")
    
    return successful == total

def main():
    """Main test function"""
    
    print("🏥 MediCare+ Existing Email Fix Test")
    print("=" * 60)
    
    # Test the specific problematic email
    single_test_success = test_existing_email_fix()
    
    # Test multiple emails
    multiple_test_success = test_multiple_existing_emails()
    
    print("\n🎯 FINAL RESULTS")
    print("=" * 60)
    
    if single_test_success and multiple_test_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Email functionality is working correctly")
        print("✅ Existing emails can receive prediction reports")
        print("✅ The 'email already exists' issue is resolved")
    elif single_test_success:
        print("✅ Main test passed, some multiple email tests failed")
        print("💡 Check individual email configurations")
    else:
        print("❌ Tests failed")
        print("💡 Check email service configuration and backend status")
    
    print("\n📝 WHAT WAS FIXED:")
    print("1. Email endpoint now handles existing emails properly")
    print("2. Database logic updated to not block existing emails")
    print("3. Email service continues even if user exists in database")
    print("4. Proper logging for existing vs new email addresses")

if __name__ == "__main__":
    main()
