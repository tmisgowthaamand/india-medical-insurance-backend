# PGRST205 Error Fix Guide - Complete Solution

## Problem
Your MediCare+ platform is showing PGRST205 error: "Could not find the table 'public.users' in the schema cache". This means the required database tables don't exist in your Supabase instance.

## Backend Service Details
- **Service ID**: srv-d3b668ogjchc73f9ece0
- **Frontend URL**: https://india-medical-insurance-frontend.vercel.app/
- **Backend URL**: https://india-medical-insurance-backend.onrender.com/

## Root Cause
The Supabase database is missing the required tables:
- `public.users`
- `public.datasets`
- `public.dataset_rows`
- `public.model_metadata`
- `public.predictions`

## Solution Options

### Option 1: Quick Fix via Supabase SQL Editor (RECOMMENDED)

1. **Go to your Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Navigate to your project: `gucyzhjyciqnvxedmoxo`

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Execute the Complete Fix Script**
   - Copy the entire content from `PGRST205_COMPLETE_FIX.sql`
   - Paste it into the SQL Editor
   - Click "Run" to execute

4. **Verify Tables Created**
   - Go to "Table Editor" in Supabase
   - You should see all 5 tables: users, datasets, dataset_rows, model_metadata, predictions

### Option 2: Automated Python Script

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install required packages**
   ```bash
   pip install supabase python-dotenv
   ```

3. **Run the fix script**
   ```bash
   python fix_database_tables.py
   ```

### Option 3: Manual Table Creation

If the above options fail, create tables manually in Supabase SQL Editor:

```sql
-- 1. Users table
CREATE TABLE public.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Datasets table
CREATE TABLE public.datasets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    columns TEXT[] NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- 3. Dataset rows table
CREATE TABLE public.dataset_rows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    dataset_id UUID REFERENCES public.datasets(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data JSONB NOT NULL
);

-- 4. Model metadata table
CREATE TABLE public.model_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_samples INTEGER,
    test_samples INTEGER,
    train_rmse FLOAT,
    test_rmse FLOAT,
    train_r2 FLOAT,
    test_r2 FLOAT,
    features TEXT[]
);

-- 5. Predictions table
CREATE TABLE public.predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    input_data JSONB NOT NULL,
    prediction FLOAT NOT NULL,
    confidence FLOAT DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default users
INSERT INTO public.users (email, password, is_admin) VALUES 
('admin@example.com', 'admin123', TRUE),
('user@example.com', 'user123', FALSE),
('demo@example.com', 'demo123', FALSE);

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';
```

## Environment Variables Verification

Ensure your Render backend has these environment variables set:

```
SUPABASE_URL=https://gucyzhjyciqnvxedmoxo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODA0MTksImV4cCI6MjA3NDQ1NjQxOX0.BYbV3CHVTrd4KzhRAFSYB7S2RiFv342f0J-Es-4pkKI
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4
ALLOWED_ORIGINS=https://india-medical-insurance-frontend.vercel.app,http://localhost:3000,*
JWT_SECRET_KEY=medical_insurance_dashboard_jwt_secret_key_2024_change_in_production
ENVIRONMENT=production
```

## Testing the Fix

1. **Test API Health**
   ```bash
   curl https://india-medical-insurance-backend.onrender.com/health
   ```

2. **Test Signup Endpoint**
   ```bash
   curl -X POST https://india-medical-insurance-backend.onrender.com/signup \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test123"}'
   ```

3. **Test Login Endpoint**
   ```bash
   curl -X POST https://india-medical-insurance-backend.onrender.com/login \
     -H "Content-Type: application/json" \
     -d "username=admin@example.com&password=admin123"
   ```

## Verification Steps

After running the fix:

1. **Check Supabase Tables**
   - Go to Supabase Dashboard → Table Editor
   - Verify all 5 tables exist with proper structure

2. **Test Frontend Connection**
   - Visit: https://india-medical-insurance-frontend.vercel.app/
   - Try to sign up or log in
   - Should work without 500 errors

3. **Check Backend Logs**
   - Go to Render Dashboard → Your Service
   - Check logs for any remaining errors

## Common Issues and Solutions

### Issue: "gen_random_uuid() function not found"
**Solution**: Use `uuid_generate_v4()` instead or enable uuid extension:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Issue: "Permission denied for table"
**Solution**: Ensure you're using the SERVICE_ROLE_KEY, not ANON_KEY

### Issue: "Schema cache not refreshed"
**Solution**: Run this in SQL Editor:
```sql
NOTIFY pgrst, 'reload schema';
```

### Issue: Still getting PGRST205 after table creation
**Solution**: 
1. Wait 2-3 minutes for cache refresh
2. Restart your Render backend service
3. Check environment variables are correctly set

## Success Indicators

✅ **Tables created successfully**
✅ **Default users inserted**
✅ **API endpoints return 200 status**
✅ **Frontend can connect without CORS errors**
✅ **Signup/Login functionality works**

## Support

If you continue to experience issues:
1. Check Supabase project logs
2. Check Render service logs
3. Verify all environment variables are set correctly
4. Ensure the Supabase project is not paused or suspended

The PGRST205 error should be completely resolved after following these steps.
