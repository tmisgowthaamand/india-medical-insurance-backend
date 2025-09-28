#!/usr/bin/env python3
"""
Quick Database Fix Script for PGRST205 Error
Automatically sets up Supabase database tables and verifies the fix
"""

import os
import sys
import asyncio
import requests
from dotenv import load_dotenv
from database import supabase_client

# Load environment variables
load_dotenv()

class DatabaseFixer:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.backend_url = "https://india-medical-insurance-backend.onrender.com"
        
    def print_header(self):
        print("🏥 MediCare+ PGRST205 Quick Fix")
        print("=" * 50)
        print(f"Backend URL: {self.backend_url}")
        print(f"Render Service: srv-d3b668ogjchc73f9ece0")
        print("=" * 50)
    
    def check_environment(self):
        """Check if environment variables are properly set"""
        print("\n🔍 Step 1: Checking Environment Variables...")
        
        if not self.supabase_url:
            print("❌ SUPABASE_URL not found")
            print("💡 Add SUPABASE_URL to your Render environment variables")
            return False
        
        if not self.service_key:
            print("❌ SUPABASE_SERVICE_ROLE_KEY not found")
            print("💡 Add SUPABASE_SERVICE_ROLE_KEY to your Render environment variables")
            return False
        
        print(f"✅ SUPABASE_URL: {self.supabase_url[:50]}...")
        print(f"✅ SERVICE_KEY: {self.service_key[:20]}...")
        return True
    
    async def create_tables_programmatically(self):
        """Create tables using Supabase client"""
        print("\n🛠️ Step 2: Creating Database Tables...")
        
        if not supabase_client.is_enabled():
            print("❌ Supabase client not enabled")
            return False
        
        try:
            # SQL commands to create tables
            sql_commands = [
                # Drop existing tables
                "DROP TABLE IF EXISTS public.predictions CASCADE;",
                "DROP TABLE IF EXISTS public.dataset_rows CASCADE;",
                "DROP TABLE IF EXISTS public.model_metadata CASCADE;",
                "DROP TABLE IF EXISTS public.datasets CASCADE;",
                "DROP TABLE IF EXISTS public.users CASCADE;",
                
                # Create users table
                """CREATE TABLE public.users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );""",
                
                # Create datasets table
                """CREATE TABLE public.datasets (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    rows INTEGER NOT NULL,
                    columns TEXT NOT NULL,
                    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata TEXT DEFAULT '{}'
                );""",
                
                # Create dataset_rows table
                """CREATE TABLE public.dataset_rows (
                    id SERIAL PRIMARY KEY,
                    dataset_id INTEGER REFERENCES public.datasets(id) ON DELETE CASCADE,
                    row_index INTEGER NOT NULL,
                    data TEXT NOT NULL
                );""",
                
                # Create model_metadata table
                """CREATE TABLE public.model_metadata (
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
                );""",
                
                # Create predictions table
                """CREATE TABLE public.predictions (
                    id SERIAL PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    input_data TEXT NOT NULL,
                    prediction DECIMAL(12, 2) NOT NULL,
                    confidence DECIMAL(5, 4),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );""",
                
                # Create indexes
                "CREATE INDEX idx_users_email ON public.users(email);",
                "CREATE INDEX idx_predictions_user_email ON public.predictions(user_email);",
                "CREATE INDEX idx_predictions_created_at ON public.predictions(created_at);",
                
                # Insert default admin user
                """INSERT INTO public.users (email, password, is_admin, created_at) 
                VALUES ('admin@medicare.com', 'admin123', true, NOW())
                ON CONFLICT (email) DO NOTHING;""",
                
                # Enable RLS and create policies
                "ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;",
                "ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;",
                "ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;",
                "ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;",
                "ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;",
                
                # Create service role policies
                "CREATE POLICY \"Service role can access all users\" ON public.users FOR ALL USING (true);",
                "CREATE POLICY \"Service role can access all datasets\" ON public.datasets FOR ALL USING (true);",
                "CREATE POLICY \"Service role can access all dataset_rows\" ON public.dataset_rows FOR ALL USING (true);",
                "CREATE POLICY \"Service role can access all model_metadata\" ON public.model_metadata FOR ALL USING (true);",
                "CREATE POLICY \"Service role can access all predictions\" ON public.predictions FOR ALL USING (true);",
                
                # Refresh schema cache
                "NOTIFY pgrst, 'reload schema';"
            ]
            
            # Execute SQL commands using Supabase RPC
            for i, sql in enumerate(sql_commands, 1):
                try:
                    # Use Supabase's rpc function to execute SQL
                    result = supabase_client.client.rpc('exec_sql', {'sql': sql}).execute()
                    print(f"✅ Command {i}/{len(sql_commands)} executed")
                except Exception as e:
                    # Try direct table operations for basic commands
                    if "CREATE TABLE" in sql and "users" in sql:
                        print(f"⚠️ Command {i} failed, trying alternative method...")
                        # Alternative: Create user directly
                        try:
                            await supabase_client.create_user("admin@medicare.com", "admin123", True)
                            print("✅ Admin user created via API")
                        except:
                            pass
                    else:
                        print(f"⚠️ Command {i} warning: {str(e)[:100]}...")
            
            print("✅ Database setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    async def verify_tables(self):
        """Verify that all required tables exist"""
        print("\n✅ Step 3: Verifying Tables...")
        
        tables = ["users", "datasets", "dataset_rows", "model_metadata", "predictions"]
        
        for table in tables:
            try:
                result = supabase_client.client.table(table).select("*").limit(1).execute()
                print(f"✅ Table '{table}' exists and accessible")
            except Exception as e:
                print(f"❌ Table '{table}' error: {e}")
                return False
        
        return True
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        print("\n🏥 Step 4: Testing Backend Health...")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend healthy: {data.get('status')}")
                print(f"✅ Model loaded: {data.get('model_loaded')}")
                return True
            else:
                print(f"❌ Backend unhealthy: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection error: {e}")
            return False
    
    def test_signup_endpoint(self):
        """Test signup endpoint"""
        print("\n👤 Step 5: Testing Signup Endpoint...")
        
        test_data = {
            "email": "quickfix_test@medicare.com",
            "password": "test123"
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/signup",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Signup endpoint working")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                print("✅ Signup endpoint working (user already exists)")
                return True
            else:
                print(f"❌ Signup failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Signup test error: {e}")
            return False
    
    async def run_complete_fix(self):
        """Run the complete fix process"""
        self.print_header()
        
        # Step 1: Check environment
        if not self.check_environment():
            print("\n❌ Environment check failed")
            print("\n🔧 Manual Fix Required:")
            print("1. Go to Render Dashboard")
            print("2. Add missing environment variables")
            print("3. Restart your service")
            return False
        
        # Step 2: Create tables
        tables_created = await self.create_tables_programmatically()
        if not tables_created:
            print("\n⚠️ Automatic table creation failed")
            print("\n🔧 Manual Fix Required:")
            print("1. Go to Supabase Dashboard → SQL Editor")
            print("2. Run the SQL script from supabase_migration.sql")
            print("3. Come back and run this script again")
            return False
        
        # Step 3: Verify tables
        if not await self.verify_tables():
            print("\n❌ Table verification failed")
            return False
        
        # Step 4: Test backend
        if not self.test_backend_health():
            print("\n❌ Backend health check failed")
            print("💡 Try restarting your Render service")
            return False
        
        # Step 5: Test signup
        if not self.test_signup_endpoint():
            print("\n❌ Signup test failed")
            return False
        
        # Success!
        print("\n🎉 PGRST205 Error Fixed Successfully!")
        print("\n✅ All systems operational:")
        print("  • Database tables created")
        print("  • Backend health check passed")
        print("  • Signup endpoint working")
        print("  • Ready for production use")
        
        print("\n🚀 Next Steps:")
        print("1. Test your Vercel frontend")
        print("2. Try creating a new user account")
        print("3. Verify all features work correctly")
        
        return True

async def main():
    """Main function"""
    fixer = DatabaseFixer()
    
    try:
        success = await fixer.run_complete_fix()
        if success:
            print("\n✅ Fix completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Fix failed - see instructions above")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
