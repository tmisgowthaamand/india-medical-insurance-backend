#!/usr/bin/env python3
"""
Test Email Error Scenarios for MediCare+ Platform
Tests various failure cases to ensure proper error messages are shown
"""

import asyncio
import os
from datetime import datetime
from fix_email_delivery_complete import EmailDeliveryFix

class EmailErrorTester:
    def __init__(self):
        print("="*70)
        print("🧪 EMAIL ERROR SCENARIOS TEST - MediCare+ Platform")
        print("="*70)
    
    async def test_invalid_credentials(self):
        """Test with invalid Gmail credentials"""
        print("🔗 TEST 1: Invalid Gmail Credentials")
        print("-" * 50)
        
        # Temporarily change credentials to invalid ones
        original_email = os.getenv("GMAIL_EMAIL")
        original_password = os.getenv("GMAIL_APP_PASSWORD")
        
        # Set invalid credentials
        os.environ["GMAIL_EMAIL"] = "invalid@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "invalidpassword"
        
        try:
            email_service = EmailDeliveryFix()
            
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
            
            result = await email_service.send_prediction_email(
                recipient_email="test@gmail.com",
                prediction_data=test_prediction,
                patient_data=test_patient_data
            )
            
            print(f"📧 Result Success: {result.get('success')}")
            print(f"📧 Result Message: {result.get('message')}")
            
            if not result.get("success") and "Gmail connection failed" in result.get("message", ""):
                print("✅ INVALID CREDENTIALS: Proper error message shown!")
                return True
            else:
                print("❌ INVALID CREDENTIALS: Error message not as expected!")
                return False
                
        finally:
            # Restore original credentials
            if original_email:
                os.environ["GMAIL_EMAIL"] = original_email
            if original_password:
                os.environ["GMAIL_APP_PASSWORD"] = original_password
    
    async def test_missing_credentials(self):
        """Test with missing Gmail credentials"""
        print("\n🔗 TEST 2: Missing Gmail Credentials")
        print("-" * 50)
        
        # Temporarily remove credentials
        original_email = os.getenv("GMAIL_EMAIL")
        original_password = os.getenv("GMAIL_APP_PASSWORD")
        
        # Remove credentials
        if "GMAIL_EMAIL" in os.environ:
            del os.environ["GMAIL_EMAIL"]
        if "GMAIL_APP_PASSWORD" in os.environ:
            del os.environ["GMAIL_APP_PASSWORD"]
        
        try:
            email_service = EmailDeliveryFix()
            
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
            
            result = await email_service.send_prediction_email(
                recipient_email="test@gmail.com",
                prediction_data=test_prediction,
                patient_data=test_patient_data
            )
            
            print(f"📧 Result Success: {result.get('success')}")
            print(f"📧 Result Message: {result.get('message')}")
            
            if not result.get("success") and "Credentials not configured" in result.get("message", ""):
                print("✅ MISSING CREDENTIALS: Proper error message shown!")
                return True
            else:
                print("❌ MISSING CREDENTIALS: Error message not as expected!")
                return False
                
        finally:
            # Restore original credentials
            if original_email:
                os.environ["GMAIL_EMAIL"] = original_email
            if original_password:
                os.environ["GMAIL_APP_PASSWORD"] = original_password
    
    async def test_invalid_email_format(self):
        """Test with invalid email format"""
        print("\n🔗 TEST 3: Invalid Email Format")
        print("-" * 50)
        
        email_service = EmailDeliveryFix()
        
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
        
        # Test with invalid email formats
        invalid_emails = [
            "invalid-email",
            "invalid@",
            "@gmail.com",
            "invalid.email.com",
            ""
        ]
        
        for invalid_email in invalid_emails:
            print(f"   Testing: {invalid_email}")
            
            result = await email_service.send_prediction_email(
                recipient_email=invalid_email,
                prediction_data=test_prediction,
                patient_data=test_patient_data
            )
            
            if not result.get("success") and "Invalid email format" in result.get("message", ""):
                print(f"   ✅ {invalid_email}: Proper error message shown!")
            else:
                print(f"   ❌ {invalid_email}: Error message not as expected!")
                print(f"   📧 Got: {result.get('message')}")
                return False
        
        print("✅ INVALID EMAIL FORMAT: All tests passed!")
        return True
    
    async def test_valid_credentials_connection(self):
        """Test connection with valid credentials"""
        print("\n🔗 TEST 4: Valid Gmail Credentials Connection")
        print("-" * 50)
        
        email_service = EmailDeliveryFix()
        connection_test = email_service.test_gmail_connection()
        
        print(f"📧 Connection Success: {connection_test.get('success')}")
        print(f"📧 Connection Message: {connection_test.get('message')}")
        
        if connection_test.get("success"):
            print("✅ VALID CREDENTIALS: Gmail connection working!")
            return True
        else:
            print("❌ VALID CREDENTIALS: Gmail connection failed!")
            print("💡 Check your Gmail credentials and internet connection")
            return False
    
    async def run_all_tests(self):
        """Run all error scenario tests"""
        print(f"🚀 Starting email error scenario tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ("Valid Credentials Connection", self.test_valid_credentials_connection()),
            ("Invalid Credentials", self.test_invalid_credentials()),
            ("Missing Credentials", self.test_missing_credentials()),
            ("Invalid Email Format", self.test_invalid_email_format())
        ]
        
        results = {}
        for test_name, test_coro in tests:
            try:
                results[test_name] = await test_coro
            except Exception as e:
                print(f"❌ {test_name}: Exception - {str(e)}")
                results[test_name] = False
        
        print("\n" + "="*70)
        print("📊 EMAIL ERROR SCENARIO TEST RESULTS")
        print("="*70)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        
        print(f"\nOverall: {total_passed}/{total_tests} tests passed")
        
        if total_passed == total_tests:
            print("🎉 ALL ERROR SCENARIO TESTS PASSED!")
            print("📧 Email service properly handles all error cases.")
        else:
            print("⚠️ Some error scenario tests failed.")
        
        print("\n💡 WHAT THIS MEANS:")
        print("✅ Users will see honest error messages when email fails")
        print("✅ No more false 'success' messages for failed emails")
        print("✅ Clear feedback helps users understand what went wrong")
        
        return results

async def main():
    """Main test function"""
    tester = EmailErrorTester()
    results = await tester.run_all_tests()
    
    print("\n🔍 EXAMPLE ERROR MESSAGES USERS WILL SEE:")
    print("-" * 50)
    print("❌ Email delivery failed to user@gmail.com")
    print("❌ Gmail connection failed: Authentication error")
    print("⏱️ Processing time: 2.1s")
    print("💡 Please try again or use Download option below")
    print()
    print("❌ Email delivery failed to user@gmail.com")
    print("❌ Invalid email format: invalid-email")
    print("⏱️ Processing time: 0.1s")
    print("💡 Please check your email address and try again")

if __name__ == "__main__":
    asyncio.run(main())
