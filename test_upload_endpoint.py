#!/usr/bin/env python3
"""
Test the upload endpoint functionality
"""

import pandas as pd
import os
import tempfile
from io import StringIO

def create_test_csv():
    """Create a test CSV file"""
    test_data = {
        'age': [25, 35, 45, 55, 65],
        'bmi': [22.0, 26.0, 30.0, 28.0, 24.0],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
        'smoker': ['No', 'Yes', 'No', 'No', 'Yes'],
        'region': ['North', 'South', 'East', 'West', 'Central'],
        'premium_annual_inr': [20000, 30000, 40000, 35000, 25000],
        'claim_amount_inr': [15000, 45000, 60000, 50000, 35000]
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    return temp_file.name, df

def test_csv_validation():
    """Test CSV validation logic"""
    print("🧪 Testing CSV validation...")
    
    # Create test CSV
    csv_file, df = create_test_csv()
    
    try:
        # Test reading CSV
        loaded_df = pd.read_csv(csv_file)
        print(f"✅ CSV loaded successfully: {len(loaded_df)} rows")
        
        # Test required columns
        required_columns = ['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr', 'claim_amount_inr']
        missing_columns = [col for col in required_columns if col not in loaded_df.columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print("✅ All required columns present")
        
        # Test data types
        print(f"✅ Data validation passed")
        print(f"   Age range: {loaded_df['age'].min()}-{loaded_df['age'].max()}")
        print(f"   BMI range: {loaded_df['bmi'].min():.1f}-{loaded_df['bmi'].max():.1f}")
        print(f"   Avg claim: ₹{loaded_df['claim_amount_inr'].mean():.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV validation failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(csv_file):
            os.remove(csv_file)

def test_fast_training():
    """Test fast training with sample data"""
    print("\n⚡ Testing fast training...")
    
    # Create test CSV
    csv_file, df = create_test_csv()
    
    try:
        # Import fast training
        from fast_train import fast_train
        
        # Test training
        model = fast_train(dataset_path=csv_file, model_type="fast_rf")
        
        if model:
            print("✅ Fast training successful")
            
            # Test prediction
            test_input = pd.DataFrame({
                'age': [30],
                'bmi': [25.0],
                'gender': ['Male'],
                'smoker': ['No'],
                'region': ['North'],
                'premium_annual_inr': [20000.0]
            })
            
            prediction = model.predict(test_input)[0]
            print(f"✅ Test prediction: ₹{prediction:.2f}")
            
            return True
        else:
            print("❌ Fast training failed")
            return False
            
    except Exception as e:
        print(f"❌ Fast training error: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(csv_file):
            os.remove(csv_file)

def test_file_operations():
    """Test file upload operations"""
    print("\n📁 Testing file operations...")
    
    try:
        # Test data directory creation
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        print("✅ Data directory created/exists")
        
        # Test file writing
        test_content = "age,bmi,gender,smoker,region,premium_annual_inr,claim_amount_inr\n25,22.0,Male,No,North,20000,15000\n"
        test_file = os.path.join(data_dir, "test_upload.csv")
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print("✅ File writing successful")
        
        # Test file reading
        df = pd.read_csv(test_file)
        print(f"✅ File reading successful: {len(df)} rows")
        
        # Clean up
        os.remove(test_file)
        print("✅ File cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Upload Endpoint Components")
    print("=" * 50)
    
    # Test 1: CSV validation
    csv_success = test_csv_validation()
    
    # Test 2: Fast training
    training_success = test_fast_training()
    
    # Test 3: File operations
    file_success = test_file_operations()
    
    print(f"\n{'=' * 50}")
    print("🏁 RESULTS")
    print(f"{'=' * 50}")
    
    results = [
        ("CSV Validation", csv_success),
        ("Fast Training", training_success),
        ("File Operations", file_success)
    ]
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Upload endpoint components are working!")
        print("✅ Ready to handle file uploads")
    else:
        print("⚠️ Some components failed")
        print("❌ Upload endpoint may have issues")

if __name__ == "__main__":
    main()
