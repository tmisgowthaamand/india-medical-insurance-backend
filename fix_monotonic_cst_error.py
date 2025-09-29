#!/usr/bin/env python3
"""
Fix monotonic_cst error on Render deployment
This script ensures all models use compatible scikit-learn parameters
"""

import os
import json
import time
from datetime import datetime
from joblib import dump, load
import pandas as pd

def backup_old_model():
    """Backup existing model if it exists"""
    model_path = "models/model_pipeline.pkl"
    
    if os.path.exists(model_path):
        backup_name = f"models/model_pipeline_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        try:
            import shutil
            shutil.copy2(model_path, backup_name)
            print(f"✅ Backed up old model to: {backup_name}")
            return True
        except Exception as e:
            print(f"⚠️ Could not backup model: {e}")
            return False
    else:
        print("ℹ️ No existing model to backup")
        return True

def force_retrain_compatible_model():
    """Force retrain with compatible parameters"""
    print("🔧 Force retraining with compatible parameters...")
    
    try:
        from fast_train import fast_train
        
        # Find dataset
        data_dir = "data"
        dataset_files = []
        
        if os.path.exists(data_dir):
            dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if not dataset_files:
            print("❌ No dataset found for training")
            return None
        
        # Use the first available dataset
        dataset_path = os.path.join(data_dir, dataset_files[0])
        print(f"📊 Using dataset: {dataset_path}")
        
        # Train with fast_rf which has compatible parameters
        new_model = fast_train(dataset_path=dataset_path, model_type="fast_rf")
        
        if new_model:
            print("✅ Compatible model trained successfully")
            
            # Test the model to ensure it works
            test_prediction = test_model_compatibility(new_model)
            if test_prediction:
                print("✅ Model compatibility test passed")
                return new_model
            else:
                print("❌ Model compatibility test failed")
                return None
        else:
            print("❌ Model training failed")
            return None
            
    except Exception as e:
        print(f"❌ Error training compatible model: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def test_model_compatibility(model):
    """Test if model works without monotonic_cst error"""
    try:
        print("🧪 Testing model compatibility...")
        
        # Create test data
        test_data = pd.DataFrame({
            'age': [30],
            'bmi': [25.0],
            'gender': ['Male'],
            'smoker': ['No'],
            'region': ['North'],
            'premium_annual_inr': [20000.0]
        })
        
        # Try prediction
        prediction = model.predict(test_data)[0]
        print(f"✅ Test prediction successful: ₹{prediction:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model compatibility test failed: {e}")
        if "monotonic_cst" in str(e):
            print("🚨 Detected monotonic_cst error - model needs retraining")
        return False

def update_requirements():
    """Update requirements.txt with compatible scikit-learn version"""
    requirements_path = "requirements.txt"
    
    try:
        # Read current requirements
        requirements = []
        if os.path.exists(requirements_path):
            with open(requirements_path, 'r') as f:
                requirements = f.readlines()
        
        # Update scikit-learn version
        updated_requirements = []
        sklearn_found = False
        
        for req in requirements:
            req = req.strip()
            if req.startswith('scikit-learn'):
                updated_requirements.append('scikit-learn>=1.3.0,<1.6.0\n')
                sklearn_found = True
                print("✅ Updated scikit-learn version constraint")
            else:
                updated_requirements.append(req + '\n' if req else '\n')
        
        # Add scikit-learn if not found
        if not sklearn_found:
            updated_requirements.append('scikit-learn>=1.3.0,<1.6.0\n')
            print("✅ Added scikit-learn version constraint")
        
        # Write updated requirements
        with open(requirements_path, 'w') as f:
            f.writelines(updated_requirements)
        
        print(f"✅ Updated {requirements_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating requirements.txt: {e}")
        return False

def create_training_metadata():
    """Create metadata about the training for debugging"""
    try:
        import sklearn
        
        metadata = {
            "training_date": datetime.now().isoformat(),
            "scikit_learn_version": sklearn.__version__,
            "model_type": "fast_rf",
            "criterion": "squared_error",
            "compatibility_fix": "monotonic_cst_error_fix",
            "optimized_for": "render_deployment"
        }
        
        os.makedirs("models", exist_ok=True)
        with open("models/training_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("✅ Created training metadata")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not create training metadata: {e}")
        return False

def main():
    """Main fix function"""
    print("🚀 Fixing monotonic_cst Error for Render Deployment")
    print("=" * 60)
    
    steps = [
        ("Backup existing model", backup_old_model),
        ("Update requirements.txt", update_requirements),
        ("Force retrain compatible model", force_retrain_compatible_model),
        ("Create training metadata", create_training_metadata)
    ]
    
    results = []
    model = None
    
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        try:
            if step_name == "Force retrain compatible model":
                result = step_func()
                if result:
                    model = result
                    results.append((step_name, True))
                else:
                    results.append((step_name, False))
            else:
                result = step_func()
                results.append((step_name, result))
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            results.append((step_name, False))
    
    print(f"\n{'=' * 60}")
    print("🏁 FIX RESULTS")
    print(f"{'=' * 60}")
    
    passed = 0
    for step_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} {step_name}")
        if success:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} steps completed")
    
    if model and passed >= 3:  # At least backup, retrain, and metadata
        print("\n🎉 MONOTONIC_CST ERROR FIX COMPLETED!")
        print("✅ Compatible model trained and saved")
        print("✅ Ready for Render deployment")
        print("\n🚀 Next steps for Render:")
        print("   1. Deploy this updated code to Render")
        print("   2. The app will automatically use the compatible model")
        print("   3. No more monotonic_cst errors!")
    else:
        print("\n⚠️ Fix incomplete - some steps failed")
        print("🔧 Manual steps needed:")
        print("   1. Check dataset availability")
        print("   2. Verify scikit-learn version compatibility")
        print("   3. Manually retrain model if needed")

if __name__ == "__main__":
    main()
