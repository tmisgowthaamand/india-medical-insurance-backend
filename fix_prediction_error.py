#!/usr/bin/env python3
"""
Fix for DecisionTreeRegressor 'monotonic_cst' attribute error
This script retrains the model with compatible scikit-learn parameters
"""

import os
import sys
from fast_train import fast_train
from joblib import load, dump
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def fix_prediction_error():
    """Fix the prediction error by retraining with compatible model"""
    print("🔧 Fixing DecisionTreeRegressor 'monotonic_cst' error...")
    print("=" * 60)
    
    # Check if we have a dataset
    data_dir = "data"
    dataset_files = []
    
    if os.path.exists(data_dir):
        dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not dataset_files:
        print("❌ No dataset files found. Cannot retrain model.")
        return False
    
    dataset_path = os.path.join(data_dir, dataset_files[0])
    print(f"📊 Using dataset: {dataset_path}")
    
    try:
        # Retrain with compatible fast RF model
        print("🚀 Retraining with compatible Random Forest model...")
        new_model = fast_train(dataset_path=dataset_path, model_type="fast_rf")
        
        if new_model:
            print("✅ Model retrained successfully with compatible parameters")
            
            # Test the new model
            print("🧪 Testing new model...")
            test_prediction(new_model)
            
            return True
        else:
            print("❌ Model retraining failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during retraining: {e}")
        return False

def test_prediction(model):
    """Test the retrained model with sample data"""
    try:
        import pandas as pd
        
        # Create test data
        test_data = pd.DataFrame({
            'age': [30, 45, 25],
            'bmi': [25.0, 28.5, 22.0],
            'gender': ['Male', 'Female', 'Male'],
            'smoker': ['No', 'Yes', 'No'],
            'region': ['North', 'South', 'East'],
            'premium_annual_inr': [15000.0, 25000.0, 12000.0]
        })
        
        # Make predictions
        predictions = model.predict(test_data)
        
        print("✅ Test predictions successful:")
        for i, pred in enumerate(predictions):
            print(f"   Sample {i+1}: ₹{pred:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test prediction failed: {e}")
        return False

def check_current_model():
    """Check if current model has the error"""
    model_path = "models/model_pipeline.pkl"
    
    if not os.path.exists(model_path):
        print("ℹ️ No existing model found")
        return False
    
    try:
        print("🔍 Checking current model...")
        model = load(model_path)
        
        # Try to access the problematic attribute
        regressor = model.named_steps['regressor']
        
        if hasattr(regressor, 'monotonic_cst'):
            print("⚠️ Current model may have compatibility issues")
            return True
        else:
            print("✅ Current model appears compatible")
            return False
            
    except Exception as e:
        print(f"⚠️ Error checking current model: {e}")
        return True  # Assume it needs fixing

def update_requirements():
    """Update requirements.txt with compatible scikit-learn version"""
    req_file = "requirements.txt"
    
    if not os.path.exists(req_file):
        print("⚠️ requirements.txt not found")
        return
    
    try:
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        # Update scikit-learn version
        updated_lines = []
        for line in lines:
            if line.startswith('scikit-learn'):
                updated_lines.append('scikit-learn>=1.3.0,<1.6.0\n')
                print("📝 Updated scikit-learn version constraint")
            else:
                updated_lines.append(line)
        
        with open(req_file, 'w') as f:
            f.writelines(updated_lines)
            
        print("✅ Requirements.txt updated")
        
    except Exception as e:
        print(f"⚠️ Could not update requirements.txt: {e}")

def main():
    """Main fix function"""
    print("🚀 DecisionTreeRegressor Compatibility Fix")
    print("=" * 60)
    
    # Step 1: Check current model
    needs_fix = check_current_model()
    
    # Step 2: Update requirements
    update_requirements()
    
    # Step 3: Retrain model with compatible parameters
    if fix_prediction_error():
        print("\n🎉 SUCCESS!")
        print("✅ Model retrained with compatible parameters")
        print("✅ Prediction error should be resolved")
        print("✅ Claims analysis should work properly")
        
        print("\n📋 Next Steps:")
        print("1. Deploy the updated code to Render")
        print("2. Test the /predict endpoint")
        print("3. Test the claims analysis functionality")
        
        return True
    else:
        print("\n❌ FAILED!")
        print("❌ Could not fix the prediction error")
        print("❌ Manual intervention may be required")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
