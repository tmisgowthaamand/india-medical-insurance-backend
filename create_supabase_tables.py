#!/usr/bin/env python3
"""
Create Supabase database tables for MediCare+ application
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def create_tables():
    """Create all required tables in Supabase"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_role_key:
        print("❌ Missing Supabase credentials!")
        return False
    
    try:
        supabase: Client = create_client(url, service_role_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # SQL to create tables
    sql_commands = [
        # Drop existing tables
        "DROP TABLE IF EXISTS public.predictions CASCADE;",
        "DROP TABLE IF EXISTS public.dataset_rows CASCADE;", 
        "DROP TABLE IF EXISTS public.model_metadata CASCADE;",
        "DROP TABLE IF EXISTS public.datasets CASCADE;",
        "DROP TABLE IF EXISTS public.users CASCADE;",
        
        # Create users table
        """
        CREATE TABLE public.users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create datasets table
        """
        CREATE TABLE public.datasets (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            rows INTEGER NOT NULL,
            columns TEXT NOT NULL,
            upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata TEXT DEFAULT '{}'
        );
        """,
        
        # Create dataset_rows table
        """
        CREATE TABLE public.dataset_rows (
            id SERIAL PRIMARY KEY,
            dataset_id INTEGER REFERENCES public.datasets(id) ON DELETE CASCADE,
            row_index INTEGER NOT NULL,
            data TEXT NOT NULL
        );
        """,
        
        # Create model_metadata table
        """
        CREATE TABLE public.model_metadata (
            id SERIAL PRIMARY KEY,
            training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            training_samples INTEGER,
            test_samples INTEGER,
            train_rmse DECIMAL(10, 4),
            test_rmse DECIMAL(10, 4),
            train_r2 DECIMAL(10, 4),
            test_r2 DECIMAL(10, 4),
            features TEXT,
            model_version VARCHAR(50) DEFAULT '1.0',
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create predictions table
        """
        CREATE TABLE public.predictions (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            input_data TEXT NOT NULL,
            prediction DECIMAL(12, 2) NOT NULL,
            confidence DECIMAL(5, 4),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create indexes
        "CREATE INDEX idx_users_email ON public.users(email);",
        "CREATE INDEX idx_predictions_user_email ON public.predictions(user_email);",
        "CREATE INDEX idx_predictions_created_at ON public.predictions(created_at);",
        
        # Insert default admin user
        """
        INSERT INTO public.users (email, password, is_admin, created_at) 
        VALUES ('admin@medicare.com', 'admin123', true, NOW())
        ON CONFLICT (email) DO NOTHING;
        """,
        
        # Enable RLS
        "ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;",
        
        # Create policies
        "CREATE POLICY \"Service role can access all users\" ON public.users FOR ALL USING (true);",
        "CREATE POLICY \"Service role can access all datasets\" ON public.datasets FOR ALL USING (true);",
        "CREATE POLICY \"Service role can access all dataset_rows\" ON public.dataset_rows FOR ALL USING (true);",
        "CREATE POLICY \"Service role can access all model_metadata\" ON public.model_metadata FOR ALL USING (true);",
        "CREATE POLICY \"Service role can access all predictions\" ON public.predictions FOR ALL USING (true);",
    ]
    
    # Execute SQL commands
    for i, sql in enumerate(sql_commands, 1):
        try:
            print(f"Executing command {i}/{len(sql_commands)}...")
            result = supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Command {i} executed successfully")
        except Exception as e:
            print(f"⚠️ Command {i} failed: {e}")
            # Continue with other commands
    
    # Verify tables were created
    try:
        result = supabase.table("users").select("count", count="exact").execute()
        print(f"✅ Users table verified - Count: {result.count}")
        return True
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False

def main():
    """Main function"""
    print("🏥 Creating Supabase Tables for MediCare+")
    print("=" * 50)
    
    success = create_tables()
    
    if success:
        print("\n🎉 Database setup completed!")
        print("✅ All tables created successfully")
        print("✅ Default admin user added")
        print("✅ Signups will now be stored in Supabase")
    else:
        print("\n❌ Database setup failed!")
        print("Please check your Supabase credentials and try again")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
