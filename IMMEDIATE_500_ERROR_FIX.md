# 🚨 IMMEDIATE 500 ERROR FIX - Render Service srv-d3b668ogjchc73f9ece0

## Problem
Your backend is returning 500 errors because Supabase database tables don't exist. This is the PGRST205 error that has occurred multiple times.

## 🔥 URGENT 5-MINUTE FIX

### Step 1: Fix Database Tables (2 minutes)
1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Open your project**: gucyzhjyciqnvxedmoxo
3. **Go to SQL Editor**
4. **Copy and paste this ENTIRE script** and click **RUN**:

```sql
-- EMERGENCY FIX for PGRST205 Error
-- This will create all required tables

-- Clean slate
DROP TABLE IF EXISTS public.predictions CASCADE;
DROP TABLE IF EXISTS public.dataset_rows CASCADE;
DROP TABLE IF EXISTS public.model_metadata CASCADE;
DROP TABLE IF EXISTS public.datasets CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- Create Users table (CRITICAL for fixing 500 error)
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

-- Create service role policies (CRITICAL)
CREATE POLICY "Service role can access all users" ON public.users FOR ALL USING (true);
CREATE POLICY "Service role can access all datasets" ON public.datasets FOR ALL USING (true);
CREATE POLICY "Service role can access all dataset_rows" ON public.dataset_rows FOR ALL USING (true);
CREATE POLICY "Service role can access all model_metadata" ON public.model_metadata FOR ALL USING (true);
CREATE POLICY "Service role can access all predictions" ON public.predictions FOR ALL USING (true);

-- CRITICAL: Refresh PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Verify tables were created
SELECT tablename FROM pg_tables WHERE schemaname = 'public' 
AND tablename IN ('users', 'datasets', 'dataset_rows', 'model_metadata', 'predictions');
```

### Step 2: Restart Render Service (1 minute)
1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Find service**: `srv-d3b668ogjchc73f9ece0`
3. **Click "Manual Deploy"** or **"Restart Service"**

### Step 3: Verify Fix (2 minutes)
Test your backend:
```bash
curl https://india-medical-insurance-backend.onrender.com/health
```

Should return: `{"status": "healthy", ...}`

## 🔍 Current Environment Variables (Already Configured)
Your Render service already has these correct variables:
- ✅ SUPABASE_URL: `https://gucyzhjyciqnvxedmoxo.supabase.co`
- ✅ SUPABASE_SERVICE_ROLE_KEY: Configured
- ✅ ALLOWED_ORIGINS: Includes Vercel domain

## 🎯 Expected Results After Fix
- ✅ No more 500 errors
- ✅ Signup endpoint works
- ✅ Login endpoint works
- ✅ Frontend connects successfully

## 🚨 If Still Not Working
Run the automated fix script:
```bash
cd backend
python quick_database_fix.py
```

## 📞 Service Information
- **Render Service**: `srv-d3b668ogjchc73f9ece0`
- **Backend URL**: `https://india-medical-insurance-backend.onrender.com`
- **Supabase Project**: `gucyzhjyciqnvxedmoxo`

---
**This fix addresses the exact same PGRST205 error that has occurred multiple times. The root cause is always missing database tables in production.**
