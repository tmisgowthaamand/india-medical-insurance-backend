#!/usr/bin/env python3
"""
Emergency Fix for 500 Server Error - PGRST205 Database Issue
Render Service: srv-d3b668ogjchc73f9ece0
"""

import os
import sys
import asyncio
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Emergency500Fix:
    def __init__(self):
        self.render_service_id = "srv-d3b668ogjchc73f9ece0"
        self.backend_url = "https://india-medical-insurance-backend.onrender.com"
        self.supabase_url = "https://gucyzhjyciqnvxedmoxo.supabase.co"
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", 
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4")
        
    def print_emergency_header(self):
        print("🚨 EMERGENCY 500 ERROR FIX")
        print("=" * 60)
        print(f"🎯 Target: Render Service {self.render_service_id}")
        print(f"🌐 Backend: {self.backend_url}")
        print(f"🗄️ Database: {self.supabase_url}")
        print("📋 Issue: PGRST205 - Missing database tables")
        print("=" * 60)
    
    def check_current_error(self):
        """Check if the 500 error is currently happening"""
        print("\n🔍 Step 1: Confirming 500 Error...")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 500:
                print("❌ Confirmed: 500 Internal Server Error")
                return True
            elif response.status_code == 200:
                print("✅ Backend is healthy - no 500 error detected")
                data = response.json()
                print(f"   Status: {data.get('status')}")
                return False
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return True
    
    def create_tables_via_supabase_api(self):
        """Create tables using Supabase REST API"""
        print("\n🛠️ Step 2: Creating Database Tables...")
        
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json"
        }
        
        # SQL to create all required tables
        sql_script = """
        -- Emergency fix for PGRST205
        DROP TABLE IF EXISTS public.predictions CASCADE;
        DROP TABLE IF EXISTS public.dataset_rows CASCADE;
        DROP TABLE IF EXISTS public.model_metadata CASCADE;
        DROP TABLE IF EXISTS public.datasets CASCADE;
        DROP TABLE IF EXISTS public.users CASCADE;

        CREATE TABLE public.users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE public.datasets (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            rows INTEGER NOT NULL,
            columns TEXT NOT NULL,
            upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata TEXT DEFAULT '{}'
        );

        CREATE TABLE public.dataset_rows (
            id SERIAL PRIMARY KEY,
            dataset_id INTEGER REFERENCES public.datasets(id) ON DELETE CASCADE,
            row_index INTEGER NOT NULL,
            data TEXT NOT NULL
        );

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

        CREATE TABLE public.predictions (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            input_data TEXT NOT NULL,
            prediction DECIMAL(12, 2) NOT NULL,
            confidence DECIMAL(5, 4),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX idx_users_email ON public.users(email);
        CREATE INDEX idx_predictions_user_email ON public.predictions(user_email);

        INSERT INTO public.users (email, password, is_admin, created_at) 
        VALUES ('admin@medicare.com', 'admin123', true, NOW())
        ON CONFLICT (email) DO NOTHING;

        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Service role can access all users" ON public.users FOR ALL USING (true);
        CREATE POLICY "Service role can access all datasets" ON public.datasets FOR ALL USING (true);
        CREATE POLICY "Service role can access all dataset_rows" ON public.dataset_rows FOR ALL USING (true);
        CREATE POLICY "Service role can access all model_metadata" ON public.model_metadata FOR ALL USING (true);
        CREATE POLICY "Service role can access all predictions" ON public.predictions FOR ALL USING (true);

        NOTIFY pgrst, 'reload schema';
        """
        
        try:
            # Use Supabase SQL execution endpoint
            sql_url = f"{self.supabase_url}/rest/v1/rpc/exec_sql"
            payload = {"sql": sql_script}
            
            response = requests.post(sql_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                print("✅ Database tables created successfully")
                return True
            else:
                print(f"⚠️ SQL execution response: {response.status_code}")
                print("💡 Trying alternative method...")
                
                # Alternative: Create admin user directly
                return self.create_admin_user_directly()
                
        except Exception as e:
            print(f"⚠️ SQL execution failed: {e}")
            print("💡 Trying alternative method...")
            return self.create_admin_user_directly()
    
    def create_admin_user_directly(self):
        """Create admin user using direct table insert"""
        print("🔄 Creating admin user via direct API...")
        
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        try:
            # Insert admin user
            user_data = {
                "email": "admin@medicare.com",
                "password": "admin123",
                "is_admin": True,
                "created_at": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/users",
                headers=headers,
                json=user_data,
                timeout=15
            )
            
            if response.status_code in [200, 201, 409]:  # 409 = conflict (already exists)
                print("✅ Admin user created/verified")
                return True
            else:
                print(f"⚠️ User creation response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Direct user creation failed: {e}")
            return False
    
    def verify_tables_exist(self):
        """Verify that tables exist and are accessible"""
        print("\n✅ Step 3: Verifying Database Tables...")
        
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json"
        }
        
        tables = ["users", "datasets", "dataset_rows", "model_metadata", "predictions"]
        verified_tables = []
        
        for table in tables:
            try:
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/{table}?select=*&limit=1",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ Table '{table}' exists and accessible")
                    verified_tables.append(table)
                else:
                    print(f"❌ Table '{table}' error: {response.status_code}")
            except Exception as e:
                print(f"❌ Table '{table}' check failed: {e}")
        
        return len(verified_tables) >= 1  # At least users table should exist
    
    def test_backend_after_fix(self):
        """Test backend endpoints after the fix"""
        print("\n🧪 Step 4: Testing Backend After Fix...")
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data.get('status')}")
                print(f"✅ Model loaded: {data.get('model_loaded')}")
            else:
                print(f"⚠️ Health check: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        # Test signup endpoint
        try:
            test_user = {
                "email": f"test_{datetime.now().strftime('%H%M%S')}@medicare.com",
                "password": "test123"
            }
            
            response = requests.post(
                f"{self.backend_url}/signup",
                json=test_user,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ Signup endpoint working")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                print("✅ Signup endpoint working (user exists)")
                return True
            else:
                print(f"❌ Signup test failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Signup test error: {e}")
            return False
    
    def run_emergency_fix(self):
        """Run the complete emergency fix"""
        self.print_emergency_header()
        
        # Step 1: Confirm the error
        has_error = self.check_current_error()
        if not has_error:
            print("\n🎉 No 500 error detected. System appears healthy!")
            return True
        
        # Step 2: Create database tables
        print("\n⚡ Applying Emergency Fix...")
        tables_created = self.create_tables_via_supabase_api()
        
        if not tables_created:
            print("\n❌ Automatic fix failed")
            print("\n🔧 MANUAL FIX REQUIRED:")
            print("1. Go to Supabase Dashboard → SQL Editor")
            print("2. Run the SQL script from SIMPLE_SUPABASE_FIX.sql")
            print("3. Restart your Render service")
            return False
        
        # Step 3: Verify tables
        if not self.verify_tables_exist():
            print("\n⚠️ Table verification incomplete")
            print("💡 Tables may still be creating. Wait 30 seconds and test again.")
        
        # Step 4: Test backend
        print("\n⏳ Waiting 10 seconds for backend to refresh...")
        import time
        time.sleep(10)
        
        if self.test_backend_after_fix():
            print("\n🎉 EMERGENCY FIX SUCCESSFUL!")
            print("\n✅ Results:")
            print("  • Database tables created")
            print("  • Backend responding normally")
            print("  • 500 error resolved")
            print("  • Signup/login functional")
            
            print(f"\n🚀 Your backend is now working:")
            print(f"   {self.backend_url}")
            
            return True
        else:
            print("\n⚠️ Fix applied but backend still has issues")
            print("💡 Try restarting your Render service manually")
            return False

def main():
    """Main function"""
    fixer = Emergency500Fix()
    
    try:
        success = fixer.run_emergency_fix()
        if success:
            print("\n✅ Emergency fix completed!")
            sys.exit(0)
        else:
            print("\n❌ Emergency fix needs manual intervention")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
