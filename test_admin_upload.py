#!/usr/bin/env python3
"""
Test admin upload functionality with sample_medical_insurance_data.csv
"""

import urllib.request
import urllib.error
import json
import os

def get_admin_token():
    """Get admin token for testing"""
    try:
        from utils import create_access_token
        admin_token = create_access_token({"sub": "admin@example.com", "is_admin": True})
        return admin_token
    except Exception as e:
        print(f"❌ Error creating admin token: {e}")
        return None

def test_csv_file():
    """Test if CSV file is valid"""
    csv_file = "data/sample_medical_insurance_data.csv"
    
    print("📁 Testing CSV file...")
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_file)
        
        print(f"✅ CSV file loaded successfully")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Check required columns
        required_columns = ['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr', 'claim_amount_inr']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print("✅ All required columns present")
        
        # Check for data issues
        print(f"   Age range: {df['age'].min()}-{df['age'].max()}")
        print(f"   BMI range: {df['bmi'].min():.1f}-{df['bmi'].max():.1f}")
        print(f"   Avg claim: ₹{df['claim_amount_inr'].mean():.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def test_fast_training():
    """Test fast training with the CSV file"""
    csv_file = "data/sample_medical_insurance_data.csv"
    
    print("\n⚡ Testing fast training...")
    
    try:
        from fast_train import fast_train
        
        model = fast_train(dataset_path=csv_file, model_type="fast_rf")
        
        if model:
            print("✅ Fast training successful")
            
            # Test prediction
            import pandas as pd
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
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def test_admin_endpoints():
    """Test admin endpoints that might be failing"""
    base_url = "http://localhost:8002"
    admin_token = get_admin_token()
    
    if not admin_token:
        print("❌ Cannot test admin endpoints without token")
        return
    
    print(f"\n🔐 Testing admin endpoints...")
    
    endpoints = [
        "/stats",
        "/live-stats", 
        "/claims-analysis",
        "/live-claims-analysis",
        "/model-status"
    ]
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            print(f"🔍 Testing: {endpoint}")
            
            req = urllib.request.Request(url)
            if 'user' in endpoint:  # Only add auth for user-specific endpoints
                req.add_header('Authorization', f'Bearer {admin_token}')
            
            with urllib.request.urlopen(req) as response:
                data = response.read()
                result = json.loads(data.decode('utf-8'))
                print(f"✅ Success")
                
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            try:
                error_body = e.read().decode('utf-8')
                error_data = json.loads(error_body)
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                pass
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Admin Upload Issues")
    print("=" * 50)
    
    # Test 1: CSV file validation
    csv_success = test_csv_file()
    
    # Test 2: Fast training
    training_success = test_fast_training()
    
    # Test 3: Admin endpoints
    test_admin_endpoints()
    
    print(f"\n{'=' * 50}")
    print("🏁 RESULTS")
    print(f"{'=' * 50}")
    
    if csv_success and training_success:
        print("🎉 CSV file and training are working!")
        print("✅ The issue might be in the upload endpoint or authentication")
        print("\n💡 Possible causes of 500 error:")
        print("   • Authentication/authorization issues")
        print("   • File upload handling problems")
        print("   • Model training timeout")
        print("   • Database storage issues")
    else:
        print("❌ Found issues with CSV or training")
        if not csv_success:
            print("   • CSV file has problems")
        if not training_success:
            print("   • Fast training is failing")

if __name__ == "__main__":
    main()
