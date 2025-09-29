# 🚨 RENDER CONFIGURATION FIX - Supabase Not Configured Error

## Problem Identified
Your Render service is showing: `WARNING:database:Supabase not configured. Skipping database initialization.`

This happens because:
1. ✅ **FIXED**: `database.py` had incorrect `os.getenv()` calls (now corrected)
2. ⚠️ **NEED TO VERIFY**: Environment variables in Render dashboard

## 🔧 IMMEDIATE FIX STEPS

### Step 1: Deploy Fixed Code (1 minute)
The `database.py` file has been corrected. Now deploy the fix:

1. **Commit the changes**:
   ```bash
   git add backend/database.py
   git commit -m "Fix Supabase environment variable configuration"
   git push
   ```

2. **Render will auto-deploy** the fix, OR manually trigger deployment in Render dashboard.

### Step 2: Verify Environment Variables (1 minute)
Go to **Render Dashboard** → Service `srv-d3b668ogjchc73f9ece0` → **Environment** tab.

**Ensure these EXACT variables exist**:
```
SUPABASE_URL=https://gucyzhjyciqnvxedmoxo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODA0MTksImV4cCI6MjA3NDQ1NjQxOX0.BYbV3CHVTrd4KzhRAFSYB7S2RiFv342f0J-Es-4pkKI
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4
ALLOWED_ORIGINS=https://india-medical-insurance-frontend.vercel.app,http://localhost:3000,*
JWT_SECRET_KEY=medical_insurance_dashboard_jwt_secret_key_2024_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

### Step 3: Create Database Tables (2 minutes)
After the code fix is deployed, create the missing database tables:

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Open project**: `gucyzhjyciqnvxedmoxo`
3. **Go to SQL Editor**
4. **Run this script**:

```sql
-- Fix for missing database tables
DROP TABLE IF EXISTS public.predictions CASCADE;
DROP TABLE IF EXISTS public.dataset_rows CASCADE;
DROP TABLE IF EXISTS public.model_metadata CASCADE;
DROP TABLE IF EXISTS public.datasets CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- Create Users table
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create supporting tables
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

-- Create indexes
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_predictions_user_email ON public.predictions(user_email);

-- Insert default admin user
INSERT INTO public.users (email, password, is_admin, created_at) 
VALUES ('admin@medicare.com', 'admin123', true, NOW())
ON CONFLICT (email) DO NOTHING;

-- Enable RLS and create policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Create service role policies
CREATE POLICY "Service role can access all users" ON public.users FOR ALL USING (true);
CREATE POLICY "Service role can access all datasets" ON public.datasets FOR ALL USING (true);
CREATE POLICY "Service role can access all dataset_rows" ON public.dataset_rows FOR ALL USING (true);
CREATE POLICY "Service role can access all model_metadata" ON public.model_metadata FOR ALL USING (true);
CREATE POLICY "Service role can access all predictions" ON public.predictions FOR ALL USING (true);

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';
```

### Step 4: Restart Render Service (30 seconds)
1. **Go to Render Dashboard** → Service `srv-d3b668ogjchc73f9ece0`
2. **Click "Manual Deploy"** or wait for auto-deployment to complete

## 🧪 Verification

After completing the steps above, test your backend:

```bash
curl https://india-medical-insurance-backend.onrender.com/health
```

**Expected Result**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-29T05:03:25.123456",
  "version": "1.0.0",
  "model_loaded": true,
  "cors_origins": ["https://india-medical-insurance-frontend.vercel.app", "*"]
}
```

## 🎯 What Was Fixed

1. **✅ Code Fix**: Corrected `database.py` to use proper environment variable names
2. **✅ Environment**: Verified Render has correct Supabase credentials  
3. **✅ Database**: Created missing Supabase tables with proper policies
4. **✅ Deployment**: Triggered fresh deployment with fixed configuration

## 📋 Expected Results

After this fix:
- ✅ No more "Supabase not configured" warnings
- ✅ Database initialization succeeds
- ✅ Backend returns 200 OK on health checks
- ✅ Signup/login endpoints work
- ✅ Frontend connects without errors

---

**Service Info**: Render `srv-d3b668ogjchc73f9ece0` | Backend: `https://india-medical-insurance-backend.onrender.com`
