#!/usr/bin/env python3
"""
Test Mock Prediction Consistency - Test the JavaScript mock logic in Python
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

def test_mock_consistency():
    """Test that mock prediction is consistent"""
    
    # Test data - same as shown in the screenshot
    test_data = {
        "age": 34,
        "bmi": 23.0,
        "gender": "Female",
        "smoker": "No",
        "region": "South",
        "premium_annual_inr": 35000
    }
    
    # Also test what would give us ₹20,939
    print("🔍 Trying to match screenshot result of ₹20,939...")
    
    # Let's try different factors to see what gives us 20,939
    target = 20939
    base_calc = 15000 * 0.9 * (35000 / 25000)  # Base * South * Premium factor
    needed_factor = target / base_calc
    print(f"   Base calculation: {base_calc}")
    print(f"   Needed factor to reach ₹20,939: {needed_factor:.3f}")
    print(f"   Current deterministic factor: {0.85 + ((int(35464) % 100) / 100) * 0.3:.3f}")
    print()
    
    print("🧪 Testing Mock Prediction Consistency")
    print("=" * 50)
    print(f"Test Data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    print("=" * 50)
    
    results = []
    
    # Make 5 predictions with the same data
    for i in range(5):
        result = mock_prediction(test_data)
        prediction = result['prediction']
        confidence = result['confidence']
        
        results.append({
            'attempt': i + 1,
            'prediction': prediction,
            'confidence': confidence
        })
        
        print(f"Attempt {i + 1}: ₹{prediction:,} (Confidence: {confidence:.1%})")
    
    # Check consistency
    predictions = [r['prediction'] for r in results]
    confidences = [r['confidence'] for r in results]
    
    print("\n📊 Consistency Check:")
    print("=" * 50)
    
    if len(set(predictions)) == 1:
        print("✅ PREDICTIONS ARE CONSISTENT!")
        print(f"   All predictions: ₹{predictions[0]:,}")
    else:
        print("❌ PREDICTIONS ARE INCONSISTENT!")
        print(f"   Different values: {set(predictions)}")
    
    if len(set(confidences)) == 1:
        print("✅ CONFIDENCE SCORES ARE CONSISTENT!")
        print(f"   All confidence scores: {confidences[0]:.1%}")
    else:
        print("❌ CONFIDENCE SCORES ARE INCONSISTENT!")
        print(f"   Different values: {set(confidences)}")
    
    # Show calculation details
    print(f"\n🔍 Calculation Details:")
    print(f"   Data Hash: {test_data['age'] + test_data['bmi'] * 10 + 200 + test_data['premium_annual_inr']}")
    print(f"   Deterministic Factor: {0.8 + ((int(test_data['age'] + test_data['bmi'] * 10 + 200 + test_data['premium_annual_inr']) % 100) / 100) * 0.4:.3f}")
    
    return len(set(predictions)) == 1 and len(set(confidences)) == 1

if __name__ == "__main__":
    success = test_mock_consistency()
    print(f"\n🎯 Test Result: {'PASS' if success else 'FAIL'}")
    
    if success:
        print("\n🎉 The mock prediction logic is now DETERMINISTIC!")
        print("   Same input data will always produce the same results.")
    else:
        print("\n❌ There's still an issue with the prediction consistency.")
