#!/usr/bin/env python3
"""
Test script for fast training functionality
"""

import time
import os
from fast_train import fast_train

def test_all_training_methods():
    """Test all fast training methods"""
    print("🧪 Testing Fast Training Methods")
    print("=" * 50)
    
    # Ensure we have a dataset
    data_path = "data/sample_medical_insurance_data.csv"
    if not os.path.exists(data_path):
        print(f"❌ Dataset not found at {data_path}")
        return False
    
    methods = [
        ("fastest", "Linear Regression - Ultra Fast"),
        ("fast_tree", "Decision Tree - Very Fast"), 
        ("fast_rf", "Random Forest - Balanced")
    ]
    
    results = []
    
    for method, description in methods:
        print(f"\n🔄 Testing {description}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            model = fast_train(dataset_path=data_path, model_type=method)
            training_time = time.time() - start_time
            
            if model:
                print(f"✅ SUCCESS - Completed in {training_time:.2f} seconds")
                results.append((method, training_time, "SUCCESS"))
            else:
                print(f"❌ FAILED - No model returned")
                results.append((method, training_time, "FAILED"))
                
        except Exception as e:
            training_time = time.time() - start_time
            print(f"❌ ERROR - {str(e)}")
            results.append((method, training_time, f"ERROR: {str(e)}"))
    
    # Summary
    print(f"\n{'=' * 50}")
    print("📊 TRAINING SPEED SUMMARY")
    print(f"{'=' * 50}")
    
    for method, time_taken, status in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"{status_icon} {method:<12} | {time_taken:>6.2f}s | {status}")
    
    # Check if all succeeded
    success_count = sum(1 for _, _, status in results if status == "SUCCESS")
    total_count = len(results)
    
    print(f"\n📈 Results: {success_count}/{total_count} methods successful")
    
    if success_count == total_count:
        print("🎉 ALL FAST TRAINING METHODS WORKING!")
        return True
    else:
        print("⚠️ Some training methods failed")
        return False

def test_model_loading():
    """Test that the saved model can be loaded"""
    print(f"\n🔍 Testing Model Loading")
    print("-" * 30)
    
    model_path = "models/model_pipeline.pkl"
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found at {model_path}")
        return False
    
    try:
        from joblib import load
        model = load(model_path)
        print(f"✅ Model loaded successfully")
        
        # Test prediction
        import pandas as pd
        test_data = pd.DataFrame({
            'age': [30],
            'bmi': [25.0],
            'gender': ['Male'],
            'smoker': ['No'],
            'region': ['North'],
            'premium_annual_inr': [15000.0]
        })
        
        prediction = model.predict(test_data)
        print(f"✅ Test prediction: ₹{prediction[0]:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Fast Training Test Suite")
    print("=" * 50)
    
    # Test 1: Training methods
    training_success = test_all_training_methods()
    
    # Test 2: Model loading
    loading_success = test_model_loading()
    
    # Final result
    print(f"\n{'=' * 50}")
    print("🏁 FINAL RESULTS")
    print(f"{'=' * 50}")
    
    if training_success and loading_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Fast training is working perfectly")
        print("✅ Admin panel retraining will be fast")
        return True
    else:
        print("❌ Some tests failed")
        print("⚠️ Check the errors above")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
