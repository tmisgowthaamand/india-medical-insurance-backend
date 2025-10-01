#!/usr/bin/env python3
"""
Insert model metadata with correct column names
"""

from database import supabase_client
from datetime import datetime, timedelta

def insert_model_data():
    """Insert model metadata with correct columns"""
    
    print("🔧 Inserting model data with correct columns...")
    
    try:
        # Sample model data using correct column names
        models_data = [
            {
                "training_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "training_samples": 1250,
                "test_samples": 250,
                "train_rmse": 3200.0,
                "test_rmse": 3500.0,
                "train_r2": 0.94,
                "test_r2": 0.92,
                "features": ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"],
                "model_version": "1.0"
            },
            {
                "training_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "training_samples": 980,
                "test_samples": 196,
                "train_rmse": 4000.0,
                "test_rmse": 4200.0,
                "train_r2": 0.91,
                "test_r2": 0.89,
                "features": ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"],
                "model_version": "1.1"
            },
            {
                "training_date": datetime.now().isoformat(),
                "training_samples": 1500,
                "test_samples": 300,
                "train_rmse": 2900.0,
                "test_rmse": 3200.0,
                "train_r2": 0.96,
                "test_r2": 0.94,
                "features": ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"],
                "model_version": "1.2"
            }
        ]
        
        # Insert each model
        for i, model_data in enumerate(models_data, 1):
            try:
                print(f"📊 Inserting model {i} (v{model_data['model_version']})...")
                
                result = supabase_client.client.table("model_metadata").insert(model_data).execute()
                
                if result.data:
                    print(f"✅ Successfully inserted model {i}")
                    print(f"   - Training samples: {model_data['training_samples']}")
                    print(f"   - Test R²: {model_data['test_r2']}")
                    print(f"   - Test RMSE: {model_data['test_rmse']}")
                else:
                    print(f"❌ Failed to insert model {i}")
                    
            except Exception as e:
                print(f"❌ Error inserting model {i}: {e}")
        
        # Verify results
        print("\n🔍 Verifying results...")
        result = supabase_client.client.table("model_metadata").select("*").execute()
        
        if result.data:
            print(f"✅ Found {len(result.data)} models in database:")
            for model in result.data:
                version = model.get('model_version', 'Unknown')
                r2 = model.get('test_r2', 'N/A')
                samples = model.get('training_samples', 'N/A')
                print(f"   - Model v{version} | Samples: {samples} | R²: {r2}")
        else:
            print("❌ No models found")
            
        return len(result.data) > 0
        
    except Exception as e:
        print(f"❌ Error in insert_model_data: {e}")
        return False

if __name__ == "__main__":
    success = insert_model_data()
    if success:
        print("\n🎉 Model metadata successfully populated!")
        print("📋 Your Supabase model_metadata table now has sample data")
        print("🔗 You can check your Supabase dashboard to see the data")
    else:
        print("\n❌ Failed to populate model metadata")
