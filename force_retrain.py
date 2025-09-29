#!/usr/bin/env python3
"""
Force retrain script to fix monotonic_cst error
This will be run automatically on startup if needed
"""

import os
import sys
from fast_train import fast_train

def force_retrain():
    """Force retrain the model with compatible parameters"""
    print("🔧 Force retraining model to fix compatibility issues...")
    
    # Find dataset
    data_dir = "data"
    dataset_files = []
    
    if os.path.exists(data_dir):
        dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not dataset_files:
        print("❌ No dataset found for retraining")
        return False
    
    dataset_path = os.path.join(data_dir, dataset_files[0])
    print(f"📊 Using dataset: {dataset_path}")
    
    try:
        # Force retrain with fast RF
        new_model = fast_train(dataset_path=dataset_path, model_type="fast_rf")
        
        if new_model:
            print("✅ Model retrained successfully")
            print("✅ monotonic_cst error should be fixed")
            return True
        else:
            print("❌ Model retraining failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during retraining: {e}")
        return False

if __name__ == "__main__":
    success = force_retrain()
    sys.exit(0 if success else 1)
