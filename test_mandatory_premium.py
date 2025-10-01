#!/usr/bin/env python3
"""
Test Mandatory Premium Field
Verifies that the premium_annual_inr field is now required in predictions
"""

import requests
import json

def test_prediction_with_premium():
    """Test prediction with premium field provided"""
    
    print("🧪 Testing Prediction with Premium Field")
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
    
    try:
        response = requests.post(
            "http://localhost:8001/predict",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction successful!")
            print(f"📈 Predicted Amount: ₹{result['prediction']:,.2f}")
            print(f"🎯 Confidence: {result['confidence']:.2%}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            try:
                error = response.json()
                print(f"📝 Error: {error}")
            except:
                print(f"📝 Error Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_prediction_without_premium():
    """Test prediction without premium field (should fail)"""
    
    print("\n🧪 Testing Prediction without Premium Field (Should Fail)")
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
    
    try:
        response = requests.post(
            "http://localhost:8001/predict",
            json=test_data,
            headers={"Content-Type": "application/json"},
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
            result = response.json()
            print(f"📈 Unexpected Result: {result}")
            return False
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_prediction_with_zero_premium():
    """Test prediction with zero premium (should work but validate range)"""
    
    print("\n🧪 Testing Prediction with Zero Premium")
    print("=" * 50)
    
    test_data = {
        "age": 35,
        "bmi": 23.0,
        "gender": "Male",
        "smoker": "No",
        "region": "East",
        "premium_annual_inr": 0.0,
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/predict",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction with zero premium successful!")
            print(f"📈 Predicted Amount: ₹{result['prediction']:,.2f}")
            print(f"🎯 Confidence: {result['confidence']:.2%}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            try:
                error = response.json()
                print(f"📝 Error: {error}")
            except:
                print(f"📝 Error Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🏥 MediCare+ Mandatory Premium Field Test")
    print("=" * 60)
    
    # Test with premium
    test1_success = test_prediction_with_premium()
    
    # Test without premium (should fail)
    test2_success = test_prediction_without_premium()
    
    # Test with zero premium
    test3_success = test_prediction_with_zero_premium()
    
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    tests_passed = sum([test1_success, test2_success, test3_success])
    total_tests = 3
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {total_tests - tests_passed}")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed!")
        print("✅ Premium field is now mandatory")
        print("✅ Validation works correctly")
        print("✅ Backend properly handles required premium")
    else:
        print("\n⚠️ Some tests failed")
        print("💡 Check backend validation and frontend form")
    
    print("\n📝 CHANGES MADE:")
    print("1. Frontend: Added 'required' attribute to premium input")
    print("2. Frontend: Updated label to show '*' (mandatory)")
    print("3. Frontend: Updated placeholder and help text")
    print("4. Backend: Changed premium_annual_inr from Optional[float] to float")
    print("5. Backend: Removed fallback to 0.0 in prediction logic")

if __name__ == "__main__":
    main()
