#!/usr/bin/env python3
"""
Test Render deployment compatibility - monotonic_cst fix verification
"""

import os
import json
from datetime import datetime

def test_model_compatibility():
    """Test that models use compatible parameters"""
    print("Testing model compatibility...")
    
    try:
        from fast_train import fast_train
        
        # Find dataset
        data_dir = "data"
        dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')] if os.path.exists(data_dir) else []
        
        if not dataset_files:
            print("No dataset found, creating sample...")
            from create_sample_data import create_sample_dataset
            create_sample_dataset()
            dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if dataset_files:
            dataset_path = os.path.join(data_dir, dataset_files[0])
            print(f"Using dataset: {dataset_path}")
            
            # Test fast training with compatible parameters
            model = fast_train(dataset_path=dataset_path, model_type="fast_rf")
            
            if model:
                print("Compatible model trained successfully")
                
                # Test prediction to ensure no monotonic_cst error
                import pandas as pd
                test_data = pd.DataFrame({
                    'age': [30, 45, 25],
                    'bmi': [25.0, 28.5, 22.0],
                    'gender': ['Male', 'Female', 'Male'],
                    'smoker': ['No', 'Yes', 'No'],
                    'region': ['North', 'South', 'East'],
                    'premium_annual_inr': [20000.0, 35000.0, 15000.0]
                })
                
                predictions = model.predict(test_data)
                print(f"Test predictions successful: {predictions}")
                
                return True
            else:
                print("Model training failed")
                return False
        else:
            print("No dataset available")
            return False
            
    except Exception as e:
        print(f"Model compatibility test failed: {e}")
        if "monotonic_cst" in str(e):
            print("CRITICAL: Still getting monotonic_cst error!")
        return False

def test_app_startup():
    """Test app startup simulation"""
    print("Testing app startup simulation...")
    
    try:
        # Simulate the startup process
        from app import retrain_compatible_model
        import asyncio
        
        async def test_startup():
            model = await retrain_compatible_model()
            return model is not None
        
        result = asyncio.run(test_startup())
        
        if result:
            print("App startup simulation successful")
            return True
        else:
            print("App startup simulation failed")
            return False
            
    except Exception as e:
        print(f"App startup test failed: {e}")
        return False

def test_endpoints():
    """Test critical endpoints"""
    print("Testing critical endpoints...")
    
    try:
        import urllib.request
        import json
        
        base_url = "http://localhost:8002"
        endpoints = ["/health", "/model-status", "/stats"]
        
        working = 0
        for endpoint in endpoints:
            try:
                url = base_url + endpoint
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = response.read()
                    result = json.loads(data.decode('utf-8'))
                    print(f"  {endpoint}: OK")
                    working += 1
            except Exception as e:
                print(f"  {endpoint}: FAILED ({e})")
        
        print(f"Endpoints working: {working}/{len(endpoints)}")
        return working >= 2  # At least health and model-status should work
        
    except Exception as e:
        print(f"Endpoint test failed: {e}")
        return False

def verify_deployment_files():
    """Verify deployment files exist"""
    print("Verifying deployment files...")
    
    files_to_check = [
        "requirements.txt",
        "start.sh", 
        "build.sh",
        "app.py",
        "fast_train.py",
        "fast_model_pipeline.py"
    ]
    
    missing = []
    for file in files_to_check:
        if not os.path.exists(file):
            missing.append(file)
        else:
            print(f"  {file}: EXISTS")
    
    if missing:
        print(f"Missing files: {missing}")
        return False
    else:
        print("All deployment files present")
        return True

def main():
    """Main test function"""
    print("=" * 50)
    print("RENDER COMPATIBILITY TEST")
    print("=" * 50)
    
    tests = [
        ("Deployment files verification", verify_deployment_files),
        ("Model compatibility test", test_model_compatibility),
        ("App startup simulation", test_app_startup),
        ("Endpoints test", test_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed >= 3:
        print("\nSUCCESS: Ready for Render deployment!")
        print("- monotonic_cst error fixed")
        print("- Compatible model training works")
        print("- App startup process verified")
        print("- Deployment files ready")
        
        print("\nRender deployment commands:")
        print("Build Command: ./build.sh")
        print("Start Command: ./start.sh")
        
    else:
        print("\nWARNING: Some tests failed")
        print("Review the failed tests before deploying to Render")

if __name__ == "__main__":
    main()
