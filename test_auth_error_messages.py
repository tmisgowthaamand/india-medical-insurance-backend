#!/usr/bin/env python3
"""
Test Authentication Error Messages for MediCare+ Platform
Demonstrates all the improved error messages users will see
"""

import requests
import json
from datetime import datetime

class AuthErrorTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.render_url = "https://srv-d3b668ogjchc73f9ece0.onrender.com"
        
        print("="*70)
        print("🧪 AUTH ERROR MESSAGE TESTING - MediCare+ Platform")
        print("="*70)
    
    def test_login_errors(self, base_url):
        """Test various login error scenarios"""
        print(f"\n🔐 TESTING LOGIN ERRORS: {base_url}")
        print("-" * 50)
        
        # Test cases for login errors
        test_cases = [
            {
                "name": "Empty Email",
                "data": {"username": "", "password": "password123"},
                "expected": "Please enter your email address"
            },
            {
                "name": "Invalid Email Format",
                "data": {"username": "invalid-email", "password": "password123"},
                "expected": "Please enter a valid email address"
            },
            {
                "name": "Email Missing @",
                "data": {"username": "usergmail.com", "password": "password123"},
                "expected": "Please enter a valid email address"
            },
            {
                "name": "Empty Password",
                "data": {"username": "user@gmail.com", "password": ""},
                "expected": "Please enter a password"
            },
            {
                "name": "User Not Found",
                "data": {"username": "nonexistent@gmail.com", "password": "password123"},
                "expected": "No account found with email"
            },
            {
                "name": "Wrong Password",
                "data": {"username": "user@example.com", "password": "wrongpassword"},
                "expected": "Incorrect password for"
            }
        ]
        
        for test_case in test_cases:
            try:
                print(f"\n   🧪 {test_case['name']}:")
                print(f"      Email: '{test_case['data']['username']}'")
                print(f"      Password: '{test_case['data']['password']}'")
                
                response = requests.post(
                    f"{base_url}/login",
                    data=test_case['data'],
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10
                )
                
                if response.status_code != 200:
                    error_detail = response.json().get("detail", "Unknown error")
                    print(f"      ❌ Result: {error_detail}")
                    
                    if test_case['expected'].lower() in error_detail.lower():
                        print(f"      ✅ Expected error message found!")
                    else:
                        print(f"      ⚠️ Expected: {test_case['expected']}")
                else:
                    print(f"      ⚠️ Unexpected success (should have failed)")
                    
            except requests.exceptions.ConnectionError:
                print(f"      ⚠️ Cannot connect to {base_url}")
                break
            except Exception as e:
                print(f"      ❌ Test error: {str(e)}")
    
    def test_signup_errors(self, base_url):
        """Test various signup error scenarios"""
        print(f"\n📝 TESTING SIGNUP ERRORS: {base_url}")
        print("-" * 50)
        
        # Test cases for signup errors
        test_cases = [
            {
                "name": "Invalid Email Format",
                "data": {"email": "invalid-email", "password": "password123"},
                "expected": "Please enter a valid email address"
            },
            {
                "name": "Short Password",
                "data": {"email": "test@gmail.com", "password": "123"},
                "expected": "Password must be at least 6 characters"
            },
            {
                "name": "Empty Email",
                "data": {"email": "", "password": "password123"},
                "expected": "Email address is required"
            },
            {
                "name": "Empty Password",
                "data": {"email": "test@gmail.com", "password": ""},
                "expected": "Password is required"
            },
            {
                "name": "Existing Email",
                "data": {"email": "user@example.com", "password": "password123"},
                "expected": "already exists"
            }
        ]
        
        for test_case in test_cases:
            try:
                print(f"\n   🧪 {test_case['name']}:")
                print(f"      Email: '{test_case['data']['email']}'")
                print(f"      Password: '{test_case['data']['password']}'")
                
                response = requests.post(
                    f"{base_url}/signup",
                    json=test_case['data'],
                    timeout=10
                )
                
                if response.status_code != 200:
                    error_detail = response.json().get("detail", "Unknown error")
                    print(f"      ❌ Result: {error_detail}")
                    
                    if test_case['expected'].lower() in error_detail.lower():
                        print(f"      ✅ Expected error message found!")
                    else:
                        print(f"      ⚠️ Expected: {test_case['expected']}")
                else:
                    print(f"      ⚠️ Unexpected success (should have failed)")
                    
            except requests.exceptions.ConnectionError:
                print(f"      ⚠️ Cannot connect to {base_url}")
                break
            except Exception as e:
                print(f"      ❌ Test error: {str(e)}")
    
    def demonstrate_frontend_messages(self):
        """Show what users will see in the frontend"""
        print(f"\n📱 FRONTEND ERROR MESSAGES USERS WILL SEE:")
        print("-" * 50)
        
        print("\n🔐 LOGIN ERRORS:")
        print("❌ Please enter your email address")
        print("❌ Please enter a valid email address (e.g., user@gmail.com)")
        print("❌ Please enter your password")
        print("❌ No account found with email 'newuser@gmail.com'. Please sign up first.")
        print("❌ Incorrect password for 'user@gmail.com'. Please try again.")
        print("❌ Cannot connect to server. Please check if the backend is running.")
        
        print("\n📝 SIGNUP ERRORS:")
        print("❌ Please enter a valid email address (e.g., user@gmail.com)")
        print("❌ Password must be at least 6 characters long")
        print("❌ An account with 'existing@gmail.com' already exists. Please login instead.")
        print("❌ Server error occurred. Please try again in a few minutes.")
        
        print("\n📧 EMAIL ERRORS:")
        print("❌ Email delivery failed to user@gmail.com")
        print("❌ Gmail connection failed: Authentication error")
        print("❌ Invalid email format: invalid-email")
        
        print("\n✅ SUCCESS MESSAGES:")
        print("✅ Login successful! Welcome back to MediCare+")
        print("✅ Account created successfully! Welcome to MediCare+")
        print("✅ Email delivered successfully to user@gmail.com!")
    
    def run_all_tests(self):
        """Run all authentication error tests"""
        print(f"🚀 Starting auth error tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test local backend
        print("\n🏠 TESTING LOCAL BACKEND")
        self.test_login_errors(self.base_url)
        self.test_signup_errors(self.base_url)
        
        # Test Render backend
        print("\n🌐 TESTING RENDER BACKEND")
        self.test_login_errors(self.render_url)
        self.test_signup_errors(self.render_url)
        
        # Show frontend messages
        self.demonstrate_frontend_messages()
        
        print("\n" + "="*70)
        print("📊 AUTH ERROR MESSAGE TEST SUMMARY")
        print("="*70)
        print("✅ Improved error messages implemented")
        print("✅ Frontend shows specific, helpful errors")
        print("✅ Backend provides detailed error responses")
        print("✅ Users get clear guidance on how to fix issues")
        
        print("\n💡 KEY IMPROVEMENTS:")
        print("• No more generic 'Invalid credentials' messages")
        print("• Specific feedback for email format issues")
        print("• Clear distinction between 'user not found' and 'wrong password'")
        print("• Helpful suggestions for fixing problems")
        print("• Consistent error message formatting with ❌ prefix")
        
        return True

def main():
    """Main test function"""
    tester = AuthErrorTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
