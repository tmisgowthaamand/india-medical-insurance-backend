#!/usr/bin/env python3
"""
Populate model_metadata table with sample data and test integration
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from database import supabase_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def populate_model_metadata():
    """Populate model_metadata table with sample training data"""
    
    print("🔄 Populating model_metadata table...")
    
    if not supabase_client.is_enabled():
        print("❌ Supabase is not enabled. Please check your .env configuration.")
        return False
    
    try:
        # Sample model metadata entries
        sample_models = [
            {
                "model_type": "RandomForestRegressor",
                "training_dataset": "india_medical_insurance_2025_synthetic.csv",
                "training_samples": 1250,
                "test_r2_score": 0.92,
                "test_rmse": 3500.0,
                "features": ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"],
                "trained_by": "admin@example.com",
                "training_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "status": "active",
                "training_type": "initial"
            },
            {
                "model_type": "RandomForestRegressor", 
                "training_dataset": "medical_insurance_updated_2025.csv",
                "training_samples": 980,
                "test_r2_score": 0.89,
                "test_rmse": 4200.0,
                "features": ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"],
                "trained_by": "admin@gmail.com",
                "training_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "status": "active",
                "training_type": "retrain"
            },
            {
                "model_type": "RandomForestRegressor",
                "training_dataset": "insurance_claims_data_2025.csv", 
                "training_samples": 1500,
                "test_r2_score": 0.94,
                "test_rmse": 3200.0,
                "features": ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"],
                "trained_by": "admin@example.com",
                "training_date": datetime.now().isoformat(),
                "status": "active",
                "training_type": "upload"
            }
        ]
        
        # Insert each model metadata entry
        for i, model_data in enumerate(sample_models, 1):
            print(f"📊 Inserting model {i}: {model_data['training_dataset']}")
            
            result = await supabase_client.store_model_metadata(model_data)
            
            if "error" in result:
                print(f"❌ Error inserting model {i}: {result['error']}")
            else:
                print(f"✅ Model {i} inserted successfully")
        
        # Verify the data was inserted
        print("\n🔍 Verifying inserted data...")
        try:
            models_result = supabase_client.client.table("model_metadata").select("*").order("created_at", desc=True).execute()
            
            if models_result.data:
                print(f"✅ Found {len(models_result.data)} models in database:")
                for model in models_result.data:
                    print(f"   - {model['model_type']} | Dataset: {model['training_dataset']} | R²: {model['test_r2_score']:.3f}")
            else:
                print("❌ No models found in database")
                
        except Exception as e:
            print(f"❌ Error verifying data: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating model metadata: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

async def populate_sample_dataset():
    """Populate datasets table with sample dataset"""
    
    print("\n🔄 Populating datasets table...")
    
    try:
        # Create sample dataset
        sample_data = {
            'age': [25, 30, 35, 40, 45, 50, 55, 60],
            'bmi': [22.5, 25.0, 27.5, 30.0, 32.5, 28.0, 26.5, 24.0],
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
            'smoker': ['No', 'No', 'Yes', 'No', 'Yes', 'No', 'Yes', 'No'],
            'region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
            'premium_annual_inr': [15000, 18000, 25000, 22000, 30000, 20000, 28000, 16000],
            'claim_amount_inr': [8000, 12000, 18000, 15000, 22000, 13000, 20000, 9000]
        }
        
        df = pd.DataFrame(sample_data)
        
        # Store in Supabase
        metadata = {
            "uploaded_by": "admin@example.com",
            "original_filename": "sample_medical_insurance_data.csv",
            "file_size": len(df) * 100  # Approximate size
        }
        
        result = await supabase_client.store_dataset("sample_medical_insurance_data.csv", df, metadata)
        
        if "error" in result:
            print(f"❌ Error storing sample dataset: {result['error']}")
        else:
            print(f"✅ Sample dataset stored with ID: {result.get('dataset_id')}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample dataset: {e}")
        return False

async def test_endpoints():
    """Test the new admin endpoints"""
    
    print("\n🧪 Testing admin endpoints...")
    
    try:
        # Test datasets endpoint
        datasets = await supabase_client.list_datasets()
        print(f"📊 Found {len(datasets)} datasets:")
        for dataset in datasets:
            print(f"   - {dataset['filename']} ({dataset['rows']} rows)")
        
        # Test model metadata retrieval
        latest_model = await supabase_client.get_latest_model_metadata()
        if latest_model:
            print(f"🤖 Latest model: {latest_model['model_type']} (R²: {latest_model['test_r2_score']:.3f})")
        else:
            print("❌ No model metadata found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

async def main():
    """Main function to populate all data"""
    
    print("🚀 Starting Supabase data population...")
    print(f"📍 Supabase URL: {os.getenv('SUPABASE_URL', 'Not set')}")
    
    # Check Supabase connection
    if not supabase_client.is_enabled():
        print("❌ Supabase connection failed. Please check your configuration.")
        return
    
    print("✅ Supabase connection successful")
    
    # Populate data
    success = True
    
    # 1. Populate sample dataset
    if not await populate_sample_dataset():
        success = False
    
    # 2. Populate model metadata
    if not await populate_model_metadata():
        success = False
    
    # 3. Test endpoints
    if not await test_endpoints():
        success = False
    
    if success:
        print("\n🎉 All data populated successfully!")
        print("📋 Summary:")
        print("   - Sample dataset added to 'datasets' table")
        print("   - Model metadata added to 'model_metadata' table")
        print("   - Admin endpoints tested and working")
        print("\n🔗 You can now:")
        print("   1. Check your Supabase dashboard to see the data")
        print("   2. Test the admin panel endpoints")
        print("   3. Upload new datasets and see them stored in Supabase")
    else:
        print("\n❌ Some operations failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
