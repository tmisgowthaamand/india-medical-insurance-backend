#!/usr/bin/env python3
"""
Test Prediction Consistency - Verify same input gives same output
"""

import requests
import json

def test_prediction_consistency():
    """Test that same input data produces same prediction results"""
    
    url = "http://localhost:8001/predict"
    
    # Test data - same as shown in the screenshot
    test_data = {
        "age": 34,
        "bmi": 23.0,
        "gender": "Female",
        "smoker": "No",
        "region": "South",
        "premium_annual_inr": 35000
    }
    
    print("🧪 Testing Prediction Consistency")
    print("=" * 50)
    print(f"Test Data: {json.dumps(test_data, indent=2)}")
    print("=" * 50)
    
    results = []
    
    # Make 5 predictions with the same data
    for i in range(5):
        try:
            response = requests.post(url, json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction')
                confidence = result.get('confidence')
                
                results.append({
                    'attempt': i + 1,
                    'prediction': prediction,
                    'confidence': confidence,
                    'mock': result.get('mock', False)
                })
                
                print(f"Attempt {i + 1}: ₹{prediction:,} (Confidence: {confidence:.1%})")
                
            else:
                print(f"Attempt {i + 1}: Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"Attempt {i + 1}: Error - {e}")
    
    # Check consistency
    if results:
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
        
        # Check if using mock or real API
        if results[0]['mock']:
            print("\n🎭 Using MOCK API (backend unavailable)")
        else:
            print("\n🚀 Using REAL API (backend connected)")
            
        return len(set(predictions)) == 1 and len(set(confidences)) == 1
    else:
        print("❌ No successful predictions made")
        return False

if __name__ == "__main__":
    success = test_prediction_consistency()
    print(f"\n🎯 Test Result: {'PASS' if success else 'FAIL'}")
