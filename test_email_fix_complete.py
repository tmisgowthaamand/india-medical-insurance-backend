#!/usr/bin/env python3
"""
COMPLETE EMAIL FIX TEST SCRIPT for MediCare+ Platform
Tests the fixed email delivery system to ensure emails actually reach Gmail inbox
"""

import asyncio
import requests
import json
from datetime import datetime

class EmailFixTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"  # Local backend
        self.render_url = "https://srv-d3b668ogjchc73f9ece0.onrender.com"  # Render backend
        
        print("="*70)
        print("🧪 EMAIL FIX COMPLETE TEST - MediCare+ Platform")
        print("="*70)
    
    def test_local_backend(self):
        """Test email functionality on local backend"""
        print("🔗 TEST 1: Local Backend Email Test")
        print("-" * 50)
        
        try:
            # Test email endpoint
            test_data = {
                "email": "perivihari8@gmail.com",
                "prediction": {
                    "prediction": 19777.48,
                    "confidence": 0.85
                },
                "patient_data": {
                    "age": 30,
                    "bmi": 25.5,
                    "gender": "Male",
                    "smoker": "No",
                    "region": "North",
                    "premium_annual_inr": 20000
                }
            }
            
            print(f"📧 Sending test email to: {test_data['email']}")
            print(f"📊 Prediction amount: ₹{test_data['prediction']['prediction']:,.0f}")
            
            response = requests.post(
                f"{self.base_url}/send-prediction-email",
                json=test_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ LOCAL BACKEND: Email sent successfully!")
                    print(f"📧 Message: {result.get('message', 'No message')}")
                    return True
                else:
                    print("❌ LOCAL BACKEND: Email failed!")
                    print(f"📧 Error: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ LOCAL BACKEND: HTTP {response.status_code}")
                print(f"📧 Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("⚠️ LOCAL BACKEND: Not running (connection refused)")
            print("💡 Start local backend with: uvicorn app:app --host 0.0.0.0 --port 8001")
            return False
        except Exception as e:
            print(f"❌ LOCAL BACKEND: Error - {str(e)}")
            return False
    
    def test_render_backend(self):
        """Test email functionality on Render backend"""
        print("\n🌐 TEST 2: Render Backend Email Test")
        print("-" * 50)
        
        try:
            # Test email endpoint
            test_data = {
                "email": "perivihari8@gmail.com",
                "prediction": {
                    "prediction": 19777.48,
                    "confidence": 0.85
                },
                "patient_data": {
                    "age": 30,
                    "bmi": 25.5,
                    "gender": "Male",
                    "smoker": "No",
                    "region": "North",
                    "premium_annual_inr": 20000
                }
            }
            
            print(f"📧 Sending test email to: {test_data['email']}")
            print(f"📊 Prediction amount: ₹{test_data['prediction']['prediction']:,.0f}")
            print("⏱️ This may take longer due to cold start...")
            
            response = requests.post(
                f"{self.render_url}/send-prediction-email",
                json=test_data,
                timeout=120  # Longer timeout for Render
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ RENDER BACKEND: Email sent successfully!")
                    print(f"📧 Message: {result.get('message', 'No message')}")
                    return True
                else:
                    print("❌ RENDER BACKEND: Email failed!")
                    print(f"📧 Error: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ RENDER BACKEND: HTTP {response.status_code}")
                print(f"📧 Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏱️ RENDER BACKEND: Timeout (>120s)")
            print("💡 Render free tier may be sleeping - try again")
            return False
        except Exception as e:
            print(f"❌ RENDER BACKEND: Error - {str(e)}")
            return False
    
    def test_gmail_credentials(self):
        """Test Gmail credentials configuration"""
        print("\n🔑 TEST 3: Gmail Credentials Check")
        print("-" * 50)
        
        try:
            # Import the email fix service
            from fix_email_delivery_complete import EmailDeliveryFix
            
            email_service = EmailDeliveryFix()
            connection_test = email_service.test_gmail_connection()
            
            if connection_test["success"]:
                print("✅ GMAIL CREDENTIALS: Valid and working!")
                print(f"📧 Sender: {email_service.sender_email}")
                print(f"🔑 Password: {'✅ SET' if email_service.sender_password else '❌ NOT SET'}")
                return True
            else:
                print("❌ GMAIL CREDENTIALS: Invalid or not working!")
                print(f"📧 Error: {connection_test.get('message', 'Unknown error')}")
                return False
                
        except ImportError:
            print("⚠️ GMAIL CREDENTIALS: Cannot import email service")
            print("💡 Make sure fix_email_delivery_complete.py is in the same directory")
            return False
        except Exception as e:
            print(f"❌ GMAIL CREDENTIALS: Error - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all email tests"""
        print(f"🚀 Starting complete email fix tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            "gmail_credentials": self.test_gmail_credentials(),
            "local_backend": self.test_local_backend(),
            "render_backend": self.test_render_backend()
        }
        
        print("\n" + "="*70)
        print("📊 EMAIL FIX TEST RESULTS")
        print("="*70)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        
        print(f"\nOverall: {total_passed}/{total_tests} tests passed")
        
        if total_passed == total_tests:
            print("🎉 ALL TESTS PASSED! Email functionality is working correctly.")
            print("📧 Users should now receive emails in their Gmail inbox.")
        else:
            print("⚠️ Some tests failed. Check the errors above and fix the issues.")
        
        print("\n💡 NEXT STEPS:")
        if results["gmail_credentials"]:
            print("✅ Gmail credentials are working")
        else:
            print("❌ Fix Gmail credentials in .env file")
        
        if results["local_backend"]:
            print("✅ Local backend email is working")
        else:
            print("❌ Start local backend or check email service")
        
        if results["render_backend"]:
            print("✅ Render backend email is working")
        else:
            print("❌ Check Render deployment and environment variables")
        
        print("\n📧 If emails are not reaching inbox:")
        print("1. Check Gmail spam folder")
        print("2. Verify Gmail credentials are correct")
        print("3. Ensure Gmail 2FA and App Password are set up")
        print("4. Check backend logs for detailed error messages")
        
        return results

def main():
    """Main test function"""
    tester = EmailFixTester()
    results = tester.run_all_tests()
    
    # Return exit code based on test results
    if all(results.values()):
        exit(0)  # All tests passed
    else:
        exit(1)  # Some tests failed

if __name__ == "__main__":
    main()
