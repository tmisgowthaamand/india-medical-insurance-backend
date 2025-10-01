#!/usr/bin/env python3
"""
Setup Supabase tables programmatically
"""

import asyncio
import os
from database import supabase_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_model_metadata_table():
    """Create model_metadata table with correct structure"""
    
    print("🔧 Creating model_metadata table...")
    
    if not supabase_client.is_enabled():
        print("❌ Supabase is not enabled. Please check your .env configuration.")
        return False
    
    try:
        # SQL to create the table
        create_table_sql = """
        -- Drop existing table if it exists
        DROP TABLE IF EXISTS public.model_metadata CASCADE;
        
        -- Create model_metadata table with all required columns
        CREATE TABLE public.model_metadata (
            id BIGSERIAL PRIMARY KEY,
            model_type TEXT NOT NULL DEFAULT 'RandomForestRegressor',
            training_dataset TEXT NOT NULL,
            training_samples INTEGER NOT NULL DEFAULT 0,
            test_r2_score FLOAT NOT NULL DEFAULT 0.0,
            test_rmse FLOAT NOT NULL DEFAULT 0.0,
            features TEXT[] DEFAULT '{}',
            trained_by TEXT NOT NULL,
            training_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            status TEXT NOT NULL DEFAULT 'active',
            training_type TEXT DEFAULT 'manual',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for better performance
        CREATE INDEX idx_model_metadata_training_date ON public.model_metadata(training_date DESC);
        CREATE INDEX idx_model_metadata_status ON public.model_metadata(status);
        CREATE INDEX idx_model_metadata_trained_by ON public.model_metadata(trained_by);
        
        -- Enable Row Level Security (RLS)
        ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
        
        -- Grant necessary permissions
        GRANT ALL ON public.model_metadata TO authenticated;
        GRANT ALL ON public.model_metadata TO service_role;
        GRANT USAGE, SELECT ON SEQUENCE model_metadata_id_seq TO authenticated;
        GRANT USAGE, SELECT ON SEQUENCE model_metadata_id_seq TO service_role;
        """
        
        # Execute the SQL
        result = supabase_client.client.rpc('exec_sql', {'sql': create_table_sql}).execute()
        
        if result.data:
            print("✅ model_metadata table created successfully")
        else:
            print("❌ Failed to create model_metadata table")
            return False
            
    except Exception as e:
        print(f"❌ Error creating table via RPC: {e}")
        
        # Try alternative method - direct table operations
        try:
            print("🔄 Trying alternative method...")
            
            # Check if table exists
            existing_tables = supabase_client.client.table('information_schema.tables').select('table_name').eq('table_schema', 'public').eq('table_name', 'model_metadata').execute()
            
            if existing_tables.data:
                print("📋 model_metadata table already exists")
            else:
                print("❌ model_metadata table does not exist and cannot be created programmatically")
                print("🔧 Please run the SQL script manually in Supabase SQL editor:")
                print("   1. Go to your Supabase dashboard")
                print("   2. Navigate to SQL Editor")
                print("   3. Run the create_model_metadata_table.sql script")
                return False
                
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            return False
    
    return True

async def insert_sample_data():
    """Insert sample model metadata"""
    
    print("📊 Inserting sample model metadata...")
    
    try:
        # Sample data
        sample_models = [
            {
                "model_type": "RandomForestRegressor",
                "training_dataset": "india_medical_insurance_2025_synthetic.csv",
                "training_samples": 1250,
                "test_r2_score": 0.92,
                "test_rmse": 3500.0,
                "features": ["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"],
                "trained_by": "admin@example.com",
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
                "status": "active",
                "training_type": "upload"
            }
        ]
        
        # Insert each record
        for i, model_data in enumerate(sample_models, 1):
            try:
                result = supabase_client.client.table("model_metadata").insert(model_data).execute()
                
                if result.data:
                    print(f"✅ Inserted model {i}: {model_data['training_dataset']}")
                else:
                    print(f"❌ Failed to insert model {i}")
                    
            except Exception as e:
                print(f"❌ Error inserting model {i}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False

async def verify_table_structure():
    """Verify the table has correct structure"""
    
    print("🔍 Verifying table structure...")
    
    try:
        # Try to select from the table
        result = supabase_client.client.table("model_metadata").select("*").limit(1).execute()
        
        if result.data is not None:
            print("✅ model_metadata table is accessible")
            
            # Check if we have any data
            count_result = supabase_client.client.table("model_metadata").select("*", count="exact").execute()
            count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            
            print(f"📊 Table contains {count} records")
            
            if count > 0:
                # Show sample record
                sample = result.data[0] if result.data else None
                if sample:
                    print(f"📋 Sample record: {sample.get('model_type', 'N/A')} | Dataset: {sample.get('training_dataset', 'N/A')}")
            
            return True
        else:
            print("❌ Cannot access model_metadata table")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying table: {e}")
        return False

async def main():
    """Main function"""
    
    print("🚀 Setting up Supabase model_metadata table...")
    
    if not supabase_client.is_enabled():
        print("❌ Supabase not enabled. Check your .env file.")
        return
    
    print("✅ Supabase connection successful")
    
    # Try to verify existing table first
    if await verify_table_structure():
        print("📋 Table already exists and is working")
        
        # Check if it has data
        try:
            result = supabase_client.client.table("model_metadata").select("*").execute()
            if not result.data:
                print("📊 Table is empty, inserting sample data...")
                await insert_sample_data()
            else:
                print(f"📊 Table already has {len(result.data)} records")
        except:
            print("📊 Inserting sample data...")
            await insert_sample_data()
    else:
        print("🔧 Table needs to be created")
        print("\n" + "="*60)
        print("MANUAL SETUP REQUIRED")
        print("="*60)
        print("The model_metadata table needs to be created manually.")
        print("\nSteps:")
        print("1. Go to your Supabase dashboard: https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to SQL Editor")
        print("4. Copy and paste the contents of 'create_model_metadata_table.sql'")
        print("5. Run the SQL script")
        print("6. Run this script again to verify")
        print("="*60)
        
        return
    
    # Final verification
    if await verify_table_structure():
        print("\n🎉 Setup completed successfully!")
        print("📋 The model_metadata table is ready for use")
        print("\n🔗 You can now:")
        print("   1. Upload datasets and they will store model metadata")
        print("   2. Check the admin panel for model history")
        print("   3. View model performance metrics")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
