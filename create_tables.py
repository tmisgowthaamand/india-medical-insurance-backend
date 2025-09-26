#!/usr/bin/env python3
"""
Database Table Creation Script for MediCare+ Platform
Run this script to create all necessary database tables
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all necessary database tables"""
    
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_key:
        logger.error("Missing Supabase credentials. Please check your .env file.")
        logger.error("Required: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(url, service_key)
        logger.info("Connected to Supabase successfully")
        
        # SQL to create tables
        create_tables_sql = """
        -- Users table
        CREATE TABLE IF NOT EXISTS public.users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Datasets table
        CREATE TABLE IF NOT EXISTS public.datasets (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            rows INTEGER NOT NULL,
            columns TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT NOW(),
            metadata TEXT DEFAULT '{}'
        );

        -- Dataset rows table
        CREATE TABLE IF NOT EXISTS public.dataset_rows (
            id SERIAL PRIMARY KEY,
            dataset_id INTEGER REFERENCES public.datasets(id) ON DELETE CASCADE,
            row_index INTEGER NOT NULL,
            data TEXT NOT NULL
        );

        -- Model metadata table
        CREATE TABLE IF NOT EXISTS public.model_metadata (
            id SERIAL PRIMARY KEY,
            training_date TIMESTAMP DEFAULT NOW(),
            training_samples INTEGER,
            test_samples INTEGER,
            train_rmse DECIMAL(10, 4),
            test_rmse DECIMAL(10, 4),
            train_r2 DECIMAL(10, 4),
            test_r2 DECIMAL(10, 4),
            features TEXT,
            model_version VARCHAR(50) DEFAULT '1.0',
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Predictions table
        CREATE TABLE IF NOT EXISTS public.predictions (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            input_data TEXT NOT NULL,
            prediction DECIMAL(12, 2) NOT NULL,
            confidence DECIMAL(5, 4),
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
        CREATE INDEX IF NOT EXISTS idx_predictions_user_email ON public.predictions(user_email);
        """
        
        # Execute table creation
        logger.info("Creating database tables...")
        result = supabase.rpc('exec_sql', {'sql': create_tables_sql}).execute()
        logger.info("Tables created successfully")
        
        # Insert default data
        logger.info("Inserting default data...")
        
        # Insert admin user
        try:
            admin_result = supabase.table("users").insert({
                "email": "admin@medicare.com",
                "password": "admin123",  # In production, hash this!
                "is_admin": True
            }).execute()
            logger.info("Default admin user created")
        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.info("Admin user already exists")
            else:
                logger.warning(f"Could not create admin user: {e}")
        
        # Insert sample model metadata
        try:
            model_result = supabase.table("model_metadata").insert({
                "training_samples": 1000,
                "test_samples": 250,
                "train_rmse": 5000.50,
                "test_rmse": 5200.75,
                "train_r2": 0.85,
                "test_r2": 0.82,
                "features": '["age", "bmi", "gender", "smoker", "region", "premium_annual_inr"]',
                "model_version": "1.0",
                "status": "active"
            }).execute()
            logger.info("Sample model metadata created")
        except Exception as e:
            logger.warning(f"Could not create sample model metadata: {e}")
        
        logger.info("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error setting up database: {e}")
        logger.error("Please check your Supabase credentials and try again.")
        return False

def verify_tables():
    """Verify that all tables exist"""
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_key:
        return False
    
    try:
        supabase = create_client(url, service_key)
        
        tables = ["users", "datasets", "dataset_rows", "model_metadata", "predictions"]
        
        for table in tables:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                logger.info(f"✅ Table '{table}' exists and is accessible")
            except Exception as e:
                logger.error(f"❌ Table '{table}' issue: {e}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        return False

if __name__ == "__main__":
    print("🏥 MediCare+ Database Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        print("Verifying database tables...")
        if verify_tables():
            print("✅ All tables verified successfully!")
        else:
            print("❌ Table verification failed!")
            sys.exit(1)
    else:
        print("Creating database tables...")
        if create_tables():
            print("\n🎉 Database setup completed!")
            print("\nNext steps:")
            print("1. Your backend should now work with the database")
            print("2. Default admin login: admin@medicare.com / admin123")
            print("3. Test your signup/login functionality")
        else:
            print("\n❌ Database setup failed!")
            print("\nTroubleshooting:")
            print("1. Check your .env file has SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
            print("2. Verify your Supabase project is active")
            print("3. Check your internet connection")
            sys.exit(1)
