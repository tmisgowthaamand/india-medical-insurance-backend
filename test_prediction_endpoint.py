#!/usr/bin/env python3
"""
Test the prediction endpoint to verify the fix
"""

import pandas as pd
from joblib import load
import os

def test_model_directly():
    """Test the model directly to ensure no monotonic_cst error"""
    print("🧪 Testing model directly...")
    
    model_path = "models/model_pipeline.pkl"
    
    if not os.path.exists(model_path):
        print("❌ Model file not found")
        return False
    
    try:
        # Load model
        model = load(model_path)
        print("✅ Model loaded successfully")
        
        # Check for problematic attributes
        regressor = model.named_steps['regressor']
        if hasattr(regressor, 'monotonic_cst'):
            print("❌ Model still has monotonic_cst attribute")
            return False
        else:
            print("✅ No monotonic_cst attribute found")
        
        # Test prediction
        test_data = pd.DataFrame({
            'age': [30, 45, 25],
            'bmi': [25.0, 28.5, 22.0],
            'gender': ['Male', 'Female', 'Male'],
            'smoker': ['No', 'Yes', 'No'],
            'region': ['North', 'South', 'East'],
            'premium_annual_inr': [15000.0, 25000.0, 12000.0]
        })
        
        predictions = model.predict(test_data)
        print("✅ Predictions successful:")
        for i, pred in enumerate(predictions):
            print(f"   Test {i+1}: ₹{pred:.2f}")
        
        return True
        
    except AttributeError as e:
        if 'monotonic_cst' in str(e):
            print(f"❌ monotonic_cst error still present: {e}")
            return False
        else:
            print(f"❌ Other AttributeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Prediction Fix")
    print("=" * 40)
    
    success = test_model_directly()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Model is compatible")
        print("✅ No monotonic_cst errors")
        print("✅ Ready for deployment")
    else:
        print("\n❌ FAILED!")
        print("❌ Model still has compatibility issues")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
