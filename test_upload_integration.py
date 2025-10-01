#!/usr/bin/env python3
"""
Test upload integration and ensure data is stored in Supabase
"""

import asyncio
import os
import pandas as pd
import numpy as np
from datetime import datetime
from database import supabase_client
from fast_train import fast_train
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_upload_workflow():
    """Test the complete upload and training workflow"""
    
    print("🧪 Testing upload workflow with Supabase integration...")
    
    if not supabase_client.is_enabled():
        print("❌ Supabase is not enabled. Please check your .env configuration.")
        return False
    
    try:
        # 1. Create a test dataset
        print("📊 Creating test dataset...")
        test_data = {
            'age': [25, 30, 35, 40, 45, 50, 55, 60, 28, 33],
            'bmi': [22.5, 25.0, 27.5, 30.0, 32.5, 28.0, 26.5, 24.0, 23.5, 26.0],
            'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
            'smoker': ['No', 'No', 'Yes', 'No', 'Yes', 'No', 'Yes', 'No', 'No', 'Yes'],
            'region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 'North', 'South'],
            'premium_annual_inr': [15000, 18000, 25000, 22000, 30000, 20000, 28000, 16000, 17000, 24000],
            'claim_amount_inr': [8000, 12000, 18000, 15000, 22000, 13000, 20000, 9000, 10000, 16000]
        }
        
        df = pd.DataFrame(test_data)
        filename = f"test_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # 2. Store dataset in Supabase
        print("💾 Storing dataset in Supabase...")
        metadata = {
            "uploaded_by": "test_user@example.com",
            "original_filename": filename,
            "file_size": len(df) * 100,
            "test_upload": True
        }
        
        dataset_result = await supabase_client.store_dataset(filename, df, metadata)
        
        if "error" in dataset_result:
            print(f"❌ Error storing dataset: {dataset_result['error']}")
            return False
        
        dataset_id = dataset_result.get('dataset_id')
        print(f"✅ Dataset stored with ID: {dataset_id}")
        
        # 3. Save dataset to local file for training
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, filename)
        df.to_csv(file_path, index=False)
        print(f"💾 Dataset saved locally: {file_path}")
        
        # 4. Train model
        print("🤖 Training model...")
        model = fast_train(dataset_path=file_path, model_type="fast_rf")
        
        if not model:
            print("❌ Model training failed")
            return False
        
        print("✅ Model trained successfully")
        
        # 5. Store model metadata
        print("📊 Storing model metadata...")
        
        # Calculate model performance metrics
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score
        
        X = df.drop('claim_amount_inr', axis=1)
        y = df['claim_amount_inr']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        model_metadata = {
            "training_samples": len(df),
            "test_samples": len(X_test),
            "train_r2": float(r2_score(y_train, model.predict(X_train))),
            "test_r2": float(r2),
            "train_rmse": float(np.sqrt(mean_squared_error(y_train, model.predict(X_train)))),
            "test_rmse": float(rmse),
            "features": list(X.columns),
            "model_version": "test_1.0",
            "training_date": datetime.now().isoformat()
        }
        
        model_result = await supabase_client.store_model_metadata(model_metadata)
        
        if "error" in model_result:
            print(f"❌ Error storing model metadata: {model_result['error']}")
            return False
        
        print("✅ Model metadata stored successfully")
        
        # 6. Verify data in Supabase
        print("🔍 Verifying data in Supabase...")
        
        # Check datasets
        datasets = await supabase_client.list_datasets()
        test_dataset = next((d for d in datasets if d['filename'] == filename), None)
        
        if test_dataset:
            print(f"✅ Dataset found: {test_dataset['filename']} ({test_dataset['rows']} rows)")
        else:
            print("❌ Dataset not found in Supabase")
            return False
        
        # Check model metadata
        latest_model = await supabase_client.get_latest_model_metadata()
        
        if latest_model and latest_model.get('model_version') == 'test_1.0':
            print(f"✅ Model metadata found: R² = {latest_model.get('test_r2', 0):.3f}, RMSE = {latest_model.get('test_rmse', 0):.1f}")
        else:
            print("❌ Model metadata not found or doesn't match")
            return False
        
        # 7. Test stats endpoint
        print("📈 Testing stats with new dataset...")
        
        # Retrieve dataset from Supabase
        retrieved_df = await supabase_client.get_dataset(filename=filename)
        
        if retrieved_df is not None:
            print(f"✅ Dataset retrieved from Supabase: {len(retrieved_df)} rows")
            
            # Calculate stats
            avg_claim = retrieved_df['claim_amount_inr'].mean()
            avg_premium = retrieved_df['premium_annual_inr'].mean()
            total_policies = len(retrieved_df)
            
            print(f"📊 Stats from Supabase data:")
            print(f"   - Avg Claim: ₹{avg_claim:,.0f}")
            print(f"   - Avg Premium: ₹{avg_premium:,.0f}")
            print(f"   - Total Policies: {total_policies}")
        else:
            print("❌ Could not retrieve dataset from Supabase")
            return False
        
        print("\n🎉 Upload workflow test completed successfully!")
        print("📋 Summary:")
        print(f"   - Dataset '{filename}' stored in Supabase")
        print(f"   - Model trained and metadata stored")
        print(f"   - R² Score: {r2:.3f}")
        print(f"   - RMSE: {rmse:.1f}")
        print(f"   - Dataset ID: {dataset_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in upload workflow test: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

async def check_supabase_tables():
    """Check if all required Supabase tables exist and have data"""
    
    print("🔍 Checking Supabase tables...")
    
    try:
        # Check datasets table
        datasets_result = supabase_client.client.table("datasets").select("*").limit(5).execute()
        print(f"📊 Datasets table: {len(datasets_result.data)} records")
        
        # Check model_metadata table
        models_result = supabase_client.client.table("model_metadata").select("*").limit(5).execute()
        print(f"🤖 Model metadata table: {len(models_result.data)} records")
        
        # Check dataset_rows table
        rows_result = supabase_client.client.table("dataset_rows").select("*").limit(5).execute()
        print(f"📋 Dataset rows table: {len(rows_result.data)} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

async def main():
    """Main function"""
    
    print("🚀 Starting Supabase integration test...")
    
    # Check connection
    if not supabase_client.is_enabled():
        print("❌ Supabase not enabled. Check your .env file.")
        return
    
    print("✅ Supabase connection successful")
    
    # Check tables
    await check_supabase_tables()
    
    # Test upload workflow
    success = await test_upload_workflow()
    
    if success:
        print("\n✅ All tests passed! Supabase integration is working correctly.")
        print("\n🔗 Next steps:")
        print("   1. Check your Supabase dashboard to see the new data")
        print("   2. Test the frontend upload functionality")
        print("   3. Verify that stats update automatically")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
