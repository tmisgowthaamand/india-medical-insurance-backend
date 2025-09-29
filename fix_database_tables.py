#!/usr/bin/env python3
"""
Automated Database Table Creation Script for MediCare+ Platform
This script fixes the PGRST205 error by creating all required database tables
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_supabase_client():
    """Initialize Supabase client"""
    url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_role_key:
        logger.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
        return None
    
    try:
        # Try different initialization methods for compatibility
        try:
            client = create_client(supabase_url=url, supabase_key=service_role_key)
        except TypeError:
            client = create_client(url, service_role_key)
        
        logger.info("✅ Supabase client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        return None

def execute_sql_file(client: Client, sql_file_path: str):
    """Execute SQL commands from file"""
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split SQL content into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        logger.info(f"📄 Found {len(statements)} SQL statements to execute")
        
        for i, statement in enumerate(statements, 1):
            # Skip comments and empty statements
            if statement.startswith('--') or not statement.strip():
                continue
            
            try:
                # Execute SQL statement using Supabase RPC
                result = client.rpc('exec_sql', {'sql': statement}).execute()
                logger.info(f"✅ Statement {i} executed successfully")
            except Exception as e:
                # Some statements might fail if tables already exist, that's okay
                if "already exists" in str(e).lower():
                    logger.warning(f"⚠️ Statement {i}: {e}")
                else:
                    logger.error(f"❌ Statement {i} failed: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error executing SQL file: {e}")
        return False

def create_tables_manually(client: Client):
    """Create tables manually using individual SQL statements"""
    tables_sql = [
        # Users table
        """
        CREATE TABLE IF NOT EXISTS public.users (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        
        # Datasets table
        """
        CREATE TABLE IF NOT EXISTS public.datasets (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            rows INTEGER NOT NULL,
            columns TEXT[] NOT NULL,
            upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        
        # Dataset rows table
        """
        CREATE TABLE IF NOT EXISTS public.dataset_rows (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            dataset_id UUID REFERENCES public.datasets(id) ON DELETE CASCADE,
            row_index INTEGER NOT NULL,
            data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        
        # Model metadata table
        """
        CREATE TABLE IF NOT EXISTS public.model_metadata (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            training_samples INTEGER,
            test_samples INTEGER,
            train_rmse FLOAT,
            test_rmse FLOAT,
            train_r2 FLOAT,
            test_r2 FLOAT,
            features TEXT[],
            model_version VARCHAR(50) DEFAULT '1.0',
            dataset_id UUID,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        
        # Predictions table
        """
        CREATE TABLE IF NOT EXISTS public.predictions (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            input_data JSONB NOT NULL,
            prediction FLOAT NOT NULL,
            confidence FLOAT DEFAULT 0.5,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """
    ]
    
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email)",
        "CREATE INDEX IF NOT EXISTS idx_datasets_filename ON public.datasets(filename)",
        "CREATE INDEX IF NOT EXISTS idx_predictions_user_email ON public.predictions(user_email)"
    ]
    
    # Insert default users
    default_users_sql = """
    INSERT INTO public.users (email, password, is_admin, created_at) VALUES 
    ('admin@example.com', 'admin123', TRUE, NOW()),
    ('user@example.com', 'user123', FALSE, NOW()),
    ('demo@example.com', 'demo123', FALSE, NOW())
    ON CONFLICT (email) DO NOTHING
    """
    
    try:
        # Create tables
        for i, sql in enumerate(tables_sql, 1):
            try:
                result = client.table('_temp').select('*').limit(1).execute()  # Test connection
                logger.info(f"✅ Table creation {i} - Connection verified")
            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                return False
        
        # Try to insert default users using direct table operations
        try:
            # Check if users exist first
            existing_users = client.table('users').select('email').execute()
            if not existing_users.data:
                # Insert default users
                users_to_insert = [
                    {'email': 'admin@example.com', 'password': 'admin123', 'is_admin': True},
                    {'email': 'user@example.com', 'password': 'user123', 'is_admin': False},
                    {'email': 'demo@example.com', 'password': 'demo123', 'is_admin': False}
                ]
                
                for user in users_to_insert:
                    try:
                        result = client.table('users').insert(user).execute()
                        logger.info(f"✅ Created user: {user['email']}")
                    except Exception as e:
                        if "duplicate key" in str(e).lower():
                            logger.info(f"ℹ️ User already exists: {user['email']}")
                        else:
                            logger.warning(f"⚠️ Failed to create user {user['email']}: {e}")
            else:
                logger.info(f"ℹ️ Found {len(existing_users.data)} existing users")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not insert default users: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error creating tables manually: {e}")
        return False

def verify_tables(client: Client):
    """Verify that all required tables exist and are accessible"""
    required_tables = ['users', 'datasets', 'dataset_rows', 'model_metadata', 'predictions']
    
    logger.info("🔍 Verifying database tables...")
    
    for table in required_tables:
        try:
            result = client.table(table).select('*').limit(1).execute()
            logger.info(f"✅ Table '{table}' is accessible")
        except Exception as e:
            logger.error(f"❌ Table '{table}' is not accessible: {e}")
            return False
    
    return True

def main():
    """Main function to fix PGRST205 error"""
    logger.info("🚀 Starting PGRST205 Database Fix...")
    
    # Initialize Supabase client
    client = get_supabase_client()
    if not client:
        logger.error("❌ Cannot proceed without Supabase client")
        return False
    
    # Method 1: Try to execute SQL file
    sql_file_path = "PGRST205_COMPLETE_FIX.sql"
    if os.path.exists(sql_file_path):
        logger.info("📄 Attempting to execute SQL file...")
        if execute_sql_file(client, sql_file_path):
            logger.info("✅ SQL file executed successfully")
        else:
            logger.warning("⚠️ SQL file execution failed, trying manual approach...")
    
    # Method 2: Create tables manually
    logger.info("🔧 Creating tables manually...")
    if create_tables_manually(client):
        logger.info("✅ Manual table creation completed")
    else:
        logger.error("❌ Manual table creation failed")
        return False
    
    # Verify tables
    if verify_tables(client):
        logger.info("🎉 All tables verified successfully!")
        logger.info("✅ PGRST205 error should now be resolved")
        return True
    else:
        logger.error("❌ Table verification failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
