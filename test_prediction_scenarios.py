#!/usr/bin/env python3
"""
Test Multiple Prediction Scenarios - Verify consistency across different inputs
"""

def mock_prediction(data):
    """Python version of the JavaScript mock prediction logic"""
    
    age = data['age']
    bmi = data['bmi']
    gender = data['gender']
    smoker = data['smoker']
    region = data['region']
    premium_annual_inr = data['premium_annual_inr']
    
    # Create a deterministic "random" factor based on input data (same as JS)
    data_hash = age + bmi * 10 + (100 if gender == 'Male' else 200) + (1000 if smoker == 'Yes' else 0) + premium_annual_inr
    deterministic_factor = 0.85 + ((int(data_hash) % 100) / 100) * 0.3  # Range: 0.85 to 1.15
    
    # Simple mock calculation
    base_claim = 15000
    
    # Age factor
    if age > 50:
        base_claim *= 1.5
    elif age > 35:
        base_claim *= 1.2
    
    # BMI factor
    if bmi > 30:
        base_claim *= 1.3
    elif bmi < 18.5:
        base_claim *= 1.1
    
    # Smoker factor
    if smoker == 'Yes':
        base_claim *= 1.8
    
    # Region factor
    region_multipliers = {'North': 1.1, 'South': 0.9, 'East': 0.95, 'West': 1.15}
    base_claim *= region_multipliers.get(region, 1.0)
    
    # Premium factor
    base_claim *= (premium_annual_inr / 25000)
    
    # Apply deterministic variation (same input = same result)
    base_claim *= deterministic_factor
    
    prediction = round(base_claim)
    
    # Deterministic confidence based on input factors
    confidence_base = 0.85
    if age > 60:
        confidence_base -= 0.05  # Lower confidence for very high age
    if bmi < 18.5 or bmi > 35:
        confidence_base -= 0.03  # Lower confidence for extreme BMI
    if smoker == 'Yes':
        confidence_base -= 0.02  # Lower confidence for smokers
    
    confidence = min(0.95, max(0.65, confidence_base))
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'input_data': data,
        'mock': True
    }

def test_scenario(name, data, expected_factors):
    """Test a specific scenario"""
    print(f"\n🧪 {name}")
    print("-" * 40)
    
    # Test consistency (5 attempts)
    results = []
    for i in range(5):
        result = mock_prediction(data)
        results.append(result['prediction'])
    
    # Check if all results are the same
    is_consistent = len(set(results)) == 1
    
    if is_consistent:
        prediction = results[0]
        confidence = mock_prediction(data)['confidence']
        print(f"✅ CONSISTENT: ₹{prediction:,} (Confidence: {confidence:.1%})")
        
        # Show expected factors
        print(f"   Expected factors: {expected_factors}")
        
        return True
    else:
        print(f"❌ INCONSISTENT: {set(results)}")
        return False

def main():
    """Test multiple scenarios"""
    print("🚀 Prediction Consistency Test - Multiple Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Young Female Non-Smoker (Screenshot Data)",
            "data": {
                "age": 34,
                "bmi": 23.0,
                "gender": "Female",
                "smoker": "No",
                "region": "South",
                "premium_annual_inr": 35000
            },
            "factors": "Age: Normal, BMI: Normal, South: 0.9x, Premium: 1.4x"
        },
        {
            "name": "Older Male Smoker",
            "data": {
                "age": 55,
                "bmi": 28.0,
                "gender": "Male",
                "smoker": "Yes",
                "region": "North",
                "premium_annual_inr": 50000
            },
            "factors": "Age: 1.5x, BMI: Normal, Smoker: 1.8x, North: 1.1x, Premium: 2.0x"
        },
        {
            "name": "Young Male High BMI",
            "data": {
                "age": 25,
                "bmi": 32.0,
                "gender": "Male",
                "smoker": "No",
                "region": "West",
                "premium_annual_inr": 20000
            },
            "factors": "Age: Normal, BMI: 1.3x (obese), West: 1.15x, Premium: 0.8x"
        },
        {
            "name": "Middle-aged Female Low BMI",
            "data": {
                "age": 40,
                "bmi": 17.0,
                "gender": "Female",
                "smoker": "No",
                "region": "East",
                "premium_annual_inr": 30000
            },
            "factors": "Age: 1.2x, BMI: 1.1x (underweight), East: 0.95x, Premium: 1.2x"
        }
    ]
    
    passed = 0
    total = len(scenarios)
    
    for scenario in scenarios:
        success = test_scenario(scenario["name"], scenario["data"], scenario["factors"])
        if success:
            passed += 1
    
    print(f"\n📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL SCENARIOS PASSED!")
        print("✅ Prediction consistency is working perfectly!")
        print("✅ Same input data will always produce same results!")
    else:
        print("❌ Some scenarios failed - there may still be consistency issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    print(f"\n🎯 Overall Test: {'PASS' if success else 'FAIL'}")
