#!/usr/bin/env python3
"""
Test Authentication Flow for Prediction
Tests the complete flow: login -> prediction with mandatory premium
"""

import requests
import json

def test_demo_login():
    """Test login with demo account"""
    
    print("🔐 Testing Demo Account Login")
    print("=" * 50)
    
    # Demo account credentials
    login_data = {
        "username": "admin@example.com",  # OAuth2 expects 'username' field
        "password": "admin123"
    }
    
    try:
        # Use form data for OAuth2 login
        response = requests.post(
            "http://localhost:8001/login",
            data=login_data,  # Use data instead of json for form encoding
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            if token:
                print("✅ Login successful!")
                print(f"📧 Email: {result.get('email', 'Unknown')}")
                print(f"👑 Admin: {result.get('is_admin', False)}")
                print(f"🔑 Token: {token[:20]}...")
                return token
            else:
                print("❌ No token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            try:
                error = response.json()
                print(f"📝 Error: {error}")
            except:
                print(f"📝 Error Text: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_authenticated_prediction(token):
    """Test prediction with authentication token"""
    
    print("\n🧪 Testing Authenticated Prediction")
    print("=" * 50)
    
    test_data = {
        "age": 35,
        "bmi": 23.0,
        "gender": "Male",
        "smoker": "No",
        "region": "East",
        "premium_annual_inr": 25000.0,
        "email": "test@example.com"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/predict",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction successful!")
            print(f"📈 Predicted Amount: ₹{result['prediction']:,.2f}")
            print(f"🎯 Confidence: {result['confidence']:.2%}")
            print(f"📋 Premium Used: ₹{result['input_data']['premium_annual_inr']:,.2f}")
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            try:
                error = response.json()
                print(f"📝 Error: {error}")
            except:
                print(f"📝 Error Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_prediction_without_premium(token):
    """Test prediction without premium (should fail validation)"""
    
    print("\n🧪 Testing Prediction without Premium (Should Fail)")
    print("=" * 60)
    
    test_data = {
        "age": 35,
        "bmi": 23.0,
        "gender": "Male",
        "smoker": "No",
        "region": "East",
        # premium_annual_inr is missing
        "email": "test@example.com"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/predict",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ Validation error as expected!")
            try:
                error = response.json()
                print(f"📝 Validation Error: {error}")
            except:
                print(f"📝 Error Text: {response.text}")
            return True
        elif response.status_code == 200:
            print("❌ Request succeeded when it should have failed!")
            return False
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🏥 MediCare+ Authentication & Prediction Flow Test")
    print("=" * 70)
    
    # Step 1: Login with demo account
    token = test_demo_login()
    
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        print("💡 Make sure the backend is running")
        print("💡 Demo accounts should work: admin@example.com / admin123")
        return
    
    # Step 2: Test authenticated prediction with premium
    prediction_success = test_authenticated_prediction(token)
    
    # Step 3: Test validation (prediction without premium)
    validation_success = test_prediction_without_premium(token)
    
    print("\n📊 TEST SUMMARY")
    print("=" * 70)
    
    tests = [
        ("Demo Account Login", token is not None),
        ("Authenticated Prediction", prediction_success),
        ("Premium Validation", validation_success)
    ]
    
    passed_tests = sum(1 for _, success in tests if success)
    total_tests = len(tests)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    print("\n📋 Detailed Results:")
    for test_name, success in tests:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 All authentication and prediction tests passed!")
        print("✅ Demo login working")
        print("✅ Authenticated predictions working")
        print("✅ Premium field validation working")
        print("✅ Frontend authentication fix should resolve 401 errors")
    else:
        print("\n⚠️ Some tests failed")
        print("💡 Check backend authentication and validation")
    
    print("\n📝 FRONTEND FIXES APPLIED:")
    print("1. ✅ Added authentication check in Prediction component")
    print("2. ✅ Redirect to login if not authenticated")
    print("3. ✅ Better error handling for 401 responses")
    print("4. ✅ Demo mode detection and messaging")
    print("5. ✅ Mandatory premium field validation")
    
    print("\n💡 DEMO ACCOUNTS AVAILABLE:")
    print("- admin@example.com / admin123 (Admin)")
    print("- admin@gmail.com / admin123 (Admin)")
    print("- user@example.com / user123 (User)")

if __name__ == "__main__":
    main()
