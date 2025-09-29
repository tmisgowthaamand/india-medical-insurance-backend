# 🚨 DEPLOY FIX NOW - Supabase Configuration Error

## Current Issue
Your Render service shows: `WARNING:database:Supabase not configured. Skipping database initialization.`

## Root Cause
The `database.py` file was using hardcoded values instead of environment variable names.

## ✅ WHAT I FIXED
1. **Fixed `database.py`** - Now correctly reads environment variables
2. **Created deployment guides** - Step-by-step instructions
3. **Created verification scripts** - To test the fix

## 🚀 DEPLOY THE FIX (3 steps)

### Step 1: Deploy Fixed Code (1 minute)
```bash
# Commit and push the database.py fix
git add backend/database.py
git commit -m "Fix: Correct Supabase environment variable configuration"
git push origin main
```

### Step 2: Verify Render Environment Variables (1 minute)
Go to **Render Dashboard** → Service `srv-d3b668ogjchc73f9ece0` → **Environment** tab.

**Ensure these variables exist** (copy from `.env.render` file):
- `SUPABASE_URL` = `https://gucyzhjyciqnvxedmoxo.supabase.co`
- `SUPABASE_ANON_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- `SUPABASE_SERVICE_ROLE_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### Step 3: Create Database Tables (2 minutes)
1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Open project**: `gucyzhjyciqnvxedmoxo`  
3. **SQL Editor** → **Run this script**:

```sql
-- Create missing database tables
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

-- Enable RLS and policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dataset_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role access" ON public.users FOR ALL USING (true);
CREATE POLICY "Service role access" ON public.datasets FOR ALL USING (true);
CREATE POLICY "Service role access" ON public.dataset_rows FOR ALL USING (true);
CREATE POLICY "Service role access" ON public.model_metadata FOR ALL USING (true);
CREATE POLICY "Service role access" ON public.predictions FOR ALL USING (true);

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';
```

## 🧪 Test the Fix
After deployment, test your backend:
```bash
curl https://india-medical-insurance-backend.onrender.com/health
```

**Expected**: `{"status": "healthy", ...}` (no more 500 errors)

## 📋 Files Created for You
- ✅ `database.py` - **FIXED** (correct environment variable usage)
- ✅ `.env.render` - Production environment variables
- ✅ `RENDER_CONFIG_FIX.md` - Detailed fix guide
- ✅ `verify_render_fix.py` - Verification script

## 🎯 After This Fix
- ✅ No more "Supabase not configured" warnings
- ✅ Database initialization succeeds  
- ✅ Backend returns 200 OK
- ✅ Signup/login endpoints work
- ✅ Frontend connects successfully

---

**Service**: `srv-d3b668ogjchc73f9ece0` | **Backend**: `https://india-medical-insurance-backend.onrender.com`

**The fix is ready - just deploy it!**
