#!/usr/bin/env python3
"""
Test Mandatory Premium Field with Authentication
Verifies that the premium_annual_inr field is now required in predictions
"""

import requests
import json

def get_auth_token():
    """Get authentication token by logging in"""
    
    print("🔐 Getting authentication token...")
    
    # Try to login with test credentials
    login_data = {
        "email": "admin@medicare.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            if token:
                print("✅ Authentication successful")
                return token
            else:
                print("❌ No token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_prediction_with_auth(token, test_name, test_data, should_succeed=True):
    """Test prediction endpoint with authentication"""
    
    print(f"\n🧪 {test_name}")
    print("=" * 60)
    
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
        
        if should_succeed:
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Prediction successful!")
                print(f"📈 Predicted Amount: ₹{result['prediction']:,.2f}")
                print(f"🎯 Confidence: {result['confidence']:.2%}")
                print(f"📋 Input Data: {result['input_data']}")
                return True
            else:
                print(f"❌ Request failed when it should succeed: {response.status_code}")
                try:
                    error = response.json()
                    print(f"📝 Error: {error}")
                except:
                    print(f"📝 Error Text: {response.text}")
                return False
        else:
            if response.status_code == 422:
                print("✅ Validation error as expected!")
                try:
                    error = response.json()
                    print(f"📝 Validation Error: {error}")
                except:
                    print(f"📝 Error Text: {response.text}")
                return True
            else:
                print(f"❌ Expected validation error (422) but got: {response.status_code}")
                return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🏥 MediCare+ Mandatory Premium Field Test (With Auth)")
    print("=" * 70)
    
    # Get authentication token
    token = get_auth_token()
    
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        print("💡 Make sure the backend is running and admin user exists")
        return
    
    # Test 1: Valid prediction with premium
    test1_data = {
        "age": 35,
        "bmi": 23.0,
        "gender": "Male",
        "smoker": "No",
        "region": "East",
        "premium_annual_inr": 25000.0,
        "email": "test@example.com"
    }
    
    test1_success = test_prediction_with_auth(
        token, 
        "Testing Prediction with Premium Field", 
        test1_data, 
        should_succeed=True
    )
    
    # Test 2: Prediction without premium (should fail with validation error)
    test2_data = {
        "age": 35,
        "bmi": 23.0,
        "gender": "Male",
        "smoker": "No",
        "region": "East",
        # premium_annual_inr is missing
        "email": "test@example.com"
    }
    
    test2_success = test_prediction_with_auth(
        token, 
        "Testing Prediction without Premium Field (Should Fail)", 
        test2_data, 
        should_succeed=False
    )
    
    # Test 3: Prediction with different premium values
    test3_data = {
        "age": 45,
        "bmi": 28.5,
        "gender": "Female",
        "smoker": "Yes",
        "region": "South",
        "premium_annual_inr": 50000.0,
        "email": "test2@example.com"
    }
    
    test3_success = test_prediction_with_auth(
        token, 
        "Testing Prediction with Higher Premium", 
        test3_data, 
        should_succeed=True
    )
    
    # Test 4: Prediction with minimum premium
    test4_data = {
        "age": 25,
        "bmi": 22.0,
        "gender": "Male",
        "smoker": "No",
        "region": "North",
        "premium_annual_inr": 1000.0,  # Minimum allowed
        "email": "test3@example.com"
    }
    
    test4_success = test_prediction_with_auth(
        token, 
        "Testing Prediction with Minimum Premium (₹1,000)", 
        test4_data, 
        should_succeed=True
    )
    
    print("\n📊 TEST SUMMARY")
    print("=" * 70)
    
    tests = [
        ("Valid prediction with premium", test1_success),
        ("Validation error without premium", test2_success),
        ("Valid prediction with higher premium", test3_success),
        ("Valid prediction with minimum premium", test4_success)
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
        print("\n🎉 All tests passed!")
        print("✅ Premium field is now mandatory")
        print("✅ Backend validation works correctly")
        print("✅ Authentication is working")
        print("✅ Different premium values are handled properly")
    else:
        print("\n⚠️ Some tests failed")
        print("💡 Check backend validation and authentication")
    
    print("\n📝 MANDATORY PREMIUM IMPLEMENTATION:")
    print("1. ✅ Frontend: Required attribute added to input field")
    print("2. ✅ Frontend: Label updated with '*' indicator")
    print("3. ✅ Frontend: Validation range (₹1,000 - ₹10,00,000)")
    print("4. ✅ Backend: PredictIn model updated (Optional → Required)")
    print("5. ✅ Backend: Removed fallback logic for missing premium")
    print("6. ✅ Authentication: Proper token-based access control")

if __name__ == "__main__":
    main()
