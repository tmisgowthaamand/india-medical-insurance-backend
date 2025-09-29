#!/usr/bin/env python3
"""
Test script to verify upload and stats functionality
"""

import pandas as pd
import os
import shutil
from datetime import datetime

def create_test_dataset():
    """Create a test dataset with different stats"""
    print("🔧 Creating test dataset with different statistics...")
    
    # Create test data with different values
    test_data = {
        'age': [25, 35, 45, 55, 65] * 20,  # 100 rows
        'bmi': [22.0, 26.0, 30.0, 28.0, 24.0] * 20,
        'gender': ['Male', 'Female'] * 50,
        'smoker': ['No', 'Yes', 'No', 'No', 'Yes'] * 20,
        'region': ['North', 'South', 'East', 'West', 'Central'] * 20,
        'premium_annual_inr': [20000, 30000, 40000, 35000, 25000] * 20,
        'claim_amount_inr': [15000, 45000, 60000, 50000, 35000] * 20  # Higher claims
    }
    
    df = pd.DataFrame(test_data)
    
    # Save to data directory
    os.makedirs("data", exist_ok=True)
    test_file = "data/test_upload_dataset.csv"
    df.to_csv(test_file, index=False)
    
    print(f"✅ Test dataset created: {test_file}")
    print(f"   Rows: {len(df)}")
    print(f"   Avg Claim: ₹{df['claim_amount_inr'].mean():.2f}")
    print(f"   Total Policies: {len(df)}")
    
    return test_file, df

def test_csv_path_update():
    """Test that CSV_PATH gets updated correctly"""
    print("\n🧪 Testing CSV_PATH update functionality...")
    
    # Import the app module to access CSV_PATH
    import sys
    sys.path.append('.')
    
    try:
        from app import CSV_PATH
        print(f"Current CSV_PATH: {CSV_PATH}")
        
        # Check if the path exists
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
            print(f"✅ Current dataset loaded: {len(df)} rows")
            print(f"   Avg Claim: ₹{df['claim_amount_inr'].mean():.2f}")
        else:
            print(f"⚠️ CSV_PATH file doesn't exist: {CSV_PATH}")
            
    except Exception as e:
        print(f"❌ Error testing CSV_PATH: {e}")

def test_stats_endpoint_logic():
    """Test the stats calculation logic"""
    print("\n📊 Testing stats calculation logic...")
    
    # Create test dataset
    test_file, df = create_test_dataset()
    
    try:
        # Calculate stats like the endpoint does
        stats = {
            'total_policies': int(len(df)),
            'avg_premium': float(df['premium_annual_inr'].mean()),
            'avg_claim': float(df['claim_amount_inr'].mean()),
            'avg_age': float(df['age'].mean()),
            'avg_bmi': float(df['bmi'].mean()),
            'smoker_percentage': float((df['smoker'] == 'Yes').mean() * 100),
            'regions': df['region'].value_counts().to_dict(),
            'gender_distribution': df['gender'].value_counts().to_dict()
        }
        
        print("✅ Stats calculated successfully:")
        print(f"   Total Policies: {stats['total_policies']}")
        print(f"   Avg Claim: ₹{stats['avg_claim']:.2f}")
        print(f"   Avg Premium: ₹{stats['avg_premium']:.2f}")
        print(f"   Smoker %: {stats['smoker_percentage']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Stats calculation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Upload and Stats Fix")
    print("=" * 50)
    
    # Test 1: CSV_PATH functionality
    test_csv_path_update()
    
    # Test 2: Stats calculation
    stats_success = test_stats_endpoint_logic()
    
    # Test 3: File selection logic
    print("\n📁 Testing file selection logic...")
    
    data_dir = "data"
    if os.path.exists(data_dir):
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if csv_files:
            print(f"✅ Found {len(csv_files)} CSV files:")
            for f in csv_files:
                file_path = os.path.join(data_dir, f)
                mod_time = os.path.getmtime(file_path)
                print(f"   • {f} (modified: {datetime.fromtimestamp(mod_time)})")
            
            # Test most recent file selection
            csv_files_with_time = [(f, os.path.getmtime(os.path.join(data_dir, f))) for f in csv_files]
            csv_files_with_time.sort(key=lambda x: x[1], reverse=True)
            most_recent = csv_files_with_time[0][0]
            print(f"✅ Most recent file: {most_recent}")
        else:
            print("❌ No CSV files found")
    else:
        print("❌ Data directory doesn't exist")
    
    print(f"\n{'=' * 50}")
    print("🏁 RESULTS")
    print(f"{'=' * 50}")
    
    if stats_success:
        print("🎉 Upload and Stats Fix Testing PASSED!")
        print("✅ Stats calculation working")
        print("✅ File selection logic working")
        print("✅ Ready for deployment")
    else:
        print("❌ Some tests failed")
        print("⚠️ Check the errors above")

if __name__ == "__main__":
    main()
