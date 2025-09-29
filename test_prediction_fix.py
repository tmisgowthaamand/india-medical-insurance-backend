#!/usr/bin/env python3
"""
Test script to verify the prediction error fix
Tests both prediction and claims analysis functionality
"""

import os
import sys
import pandas as pd
from joblib import load
import json

def test_model_loading():
    """Test that the model loads without errors"""
    print("🔍 Testing Model Loading...")
    print("-" * 40)
    
    model_path = "models/model_pipeline.pkl"
    
    if not os.path.exists(model_path):
        print("❌ Model file not found")
        return False
    
    try:
        model = load(model_path)
        print("✅ Model loaded successfully")
        
        # Check model type
        regressor = model.named_steps['regressor']
        model_type = type(regressor).__name__
        print(f"✅ Model type: {model_type}")
        
        # Check for problematic attributes
        if hasattr(regressor, 'monotonic_cst'):
            print("⚠️ Model still has monotonic_cst attribute")
        else:
            print("✅ No monotonic_cst attribute found")
        
        return model
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_prediction_functionality(model):
    """Test prediction with various input scenarios"""
    print("\n🧪 Testing Prediction Functionality...")
    print("-" * 40)
    
    # Test cases
    test_cases = [
        {
            "name": "Young Non-Smoker",
            "data": {
                'age': 25,
                'bmi': 22.0,
                'gender': 'Male',
                'smoker': 'No',
                'region': 'North',
                'premium_annual_inr': 12000.0
            }
        },
        {
            "name": "Middle-aged Smoker",
            "data": {
                'age': 45,
                'bmi': 28.5,
                'gender': 'Female',
                'smoker': 'Yes',
                'region': 'South',
                'premium_annual_inr': 25000.0
            }
        },
        {
            "name": "Senior Non-Smoker",
            "data": {
                'age': 60,
                'bmi': 26.0,
                'gender': 'Male',
                'smoker': 'No',
                'region': 'East',
                'premium_annual_inr': 30000.0
            }
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\nTest {i}: {test_case['name']}")
            
            # Create DataFrame
            test_df = pd.DataFrame([test_case['data']])
            
            # Make prediction
            prediction = model.predict(test_df)[0]
            
            print(f"   Input: Age={test_case['data']['age']}, BMI={test_case['data']['bmi']}, Smoker={test_case['data']['smoker']}")
            print(f"   ✅ Prediction: ₹{prediction:.2f}")
            
            # Validate prediction is reasonable
            if 1000 <= prediction <= 100000:
                print(f"   ✅ Prediction is within reasonable range")
                success_count += 1
            else:
                print(f"   ⚠️ Prediction seems unreasonable")
            
        except Exception as e:
            print(f"   ❌ Prediction failed: {e}")
    
    print(f"\n📊 Prediction Tests: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)

def test_claims_analysis():
    """Test claims analysis functionality"""
    print("\n📈 Testing Claims Analysis...")
    print("-" * 40)
    
    # Find dataset
    data_dir = "data"
    dataset_files = []
    
    if os.path.exists(data_dir):
        dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not dataset_files:
        print("❌ No dataset found for claims analysis")
        return False
    
    dataset_path = os.path.join(data_dir, dataset_files[0])
    
    try:
        # Load dataset
        df = pd.read_csv(dataset_path)
        print(f"✅ Dataset loaded: {len(df)} rows")
        
        # Test age group analysis
        df['age_group'] = pd.cut(df['age'], bins=[0, 30, 40, 50, 60, 100], labels=['<30', '30-40', '40-50', '50-60', '60+'])
        age_groups = df.groupby('age_group').agg({
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        print("✅ Age group analysis completed")
        
        # Test region analysis
        region_analysis = df.groupby('region').agg({
            'claim_amount_inr': ['mean', 'count'],
            'premium_annual_inr': 'mean'
        }).to_dict()
        print("✅ Region analysis completed")
        
        # Test smoker analysis
        smoker_analysis = df.groupby('smoker').agg({
            'claim_amount_inr': 'mean',
            'premium_annual_inr': 'mean'
        }).to_dict()
        print("✅ Smoker analysis completed")
        
        # Test premium vs claims correlation
        premium_bins = pd.qcut(df['premium_annual_inr'], q=5, labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
        premium_vs_claims = df.groupby(premium_bins)['claim_amount_inr'].mean().to_dict()
        print("✅ Premium vs claims analysis completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Claims analysis failed: {e}")
        return False

def test_api_compatibility():
    """Test API endpoint compatibility"""
    print("\n🔌 Testing API Compatibility...")
    print("-" * 40)
    
    try:
        # Import the app modules to check for import errors
        from fast_model_pipeline import build_fast_pipeline, get_feature_importance
        from fast_train import fast_train
        print("✅ Fast model modules import successfully")
        
        # Test building a pipeline
        pipeline = build_fast_pipeline("fast_rf")
        print("✅ Fast pipeline builds successfully")
        
        # Check model metadata
        metadata_path = "models/training_metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            print(f"✅ Training metadata available: {metadata.get('model_type', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ API compatibility test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Prediction Error Fix Verification")
    print("=" * 50)
    
    # Test 1: Model loading
    model = test_model_loading()
    if not model:
        print("\n❌ CRITICAL: Model loading failed")
        return False
    
    # Test 2: Prediction functionality
    prediction_success = test_prediction_functionality(model)
    
    # Test 3: Claims analysis
    claims_success = test_claims_analysis()
    
    # Test 4: API compatibility
    api_success = test_api_compatibility()
    
    # Final results
    print(f"\n{'=' * 50}")
    print("🏁 FINAL TEST RESULTS")
    print(f"{'=' * 50}")
    
    tests = [
        ("Model Loading", model is not False),
        ("Prediction Functionality", prediction_success),
        ("Claims Analysis", claims_success),
        ("API Compatibility", api_success)
    ]
    
    passed_tests = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 Overall: {passed_tests}/{len(tests)} tests passed")
    
    if passed_tests == len(tests):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ DecisionTreeRegressor error is fixed")
        print("✅ Prediction functionality works")
        print("✅ Claims analysis works")
        print("✅ Ready for deployment")
        return True
    else:
        print("\n⚠️ Some tests failed")
        print("❌ Additional fixes may be needed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
