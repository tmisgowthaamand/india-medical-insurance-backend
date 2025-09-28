# PGRST205 Error Complete Fix Guide
## "Could not find the table 'public.users' in the schema cache"

🚨 **Error Context**: Your Render backend (srv-d3b668ogjchc73f9ece0) is showing PGRST205 errors when users try to signup, indicating missing Supabase database tables.

## 🔍 Root Cause
The PGRST205 error occurs when:
1. Supabase database tables don't exist in production
2. PostgREST schema cache is outdated
3. Row Level Security (RLS) policies are blocking access
4. Environment variables are incorrect

## 🛠️ Complete Fix Solution

### Step 1: Run SQL Migration in Supabase
1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard
2. **Navigate to**: Your project → SQL Editor
3. **Copy and paste** the complete migration script from `supabase_migration.sql`
4. **Click "Run"** to execute the migration

### Step 2: Verify Environment Variables in Render
1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Find your service**: `srv-d3b668ogjchc73f9ece0`
3. **Go to**: Environment tab
4. **Verify these variables exist**:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ALLOWED_ORIGINS=https://india-medical-insurance-frontend.vercel.app,*
   ```

### Step 3: Restart Render Service
1. **In Render Dashboard** → Your service
2. **Click "Manual Deploy"** or **"Restart Service"**
3. **Wait for deployment** to complete

### Step 4: Test the Fix
Run the verification script:
```bash
cd backend
python verify_supabase_setup.py
```

## 🚀 Quick Fix Script
If you need an automated solution, run:
```bash
cd backend
python quick_database_fix.py
```

## 🔧 Manual Verification Steps

### Test 1: Check API Health
```bash
curl https://india-medical-insurance-backend.onrender.com/health
```
Should return: `{"status": "healthy", ...}`

### Test 2: Test Signup Endpoint
```bash
curl -X POST https://india-medical-insurance-backend.onrender.com/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```
Should return: `{"message": "User created successfully", ...}`

### Test 3: Verify Tables in Supabase
In Supabase SQL Editor, run:
```sql
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'datasets', 'dataset_rows', 'model_metadata', 'predictions');
```

## 📋 Expected Results After Fix

✅ **Backend Health Check**: Returns 200 OK  
✅ **Signup Endpoint**: Creates users successfully  
✅ **Login Endpoint**: Authenticates users  
✅ **Database Tables**: All 5 tables exist and accessible  
✅ **Frontend Connection**: Vercel app connects without CORS errors  

## 🔍 Troubleshooting Common Issues

### Issue 1: "Service role key not found"
**Solution**: Check environment variables in Render dashboard

### Issue 2: "CORS error"
**Solution**: Verify ALLOWED_ORIGINS includes your Vercel domain

### Issue 3: "Tables still not found"
**Solution**: Run `NOTIFY pgrst, 'reload schema';` in Supabase SQL Editor

### Issue 4: "RLS policy blocking access"
**Solution**: Ensure service role policies are created (included in migration)

## 📞 Support Information

- **Render Service ID**: `srv-d3b668ogjchc73f9ece0`
- **Backend URL**: `https://india-medical-insurance-backend.onrender.com`
- **Frontend URL**: `https://india-medical-insurance-frontend.vercel.app`

## 🎯 Success Indicators

After applying this fix, you should see:
1. ✅ No more PGRST205 errors in logs
2. ✅ Successful user signup/login
3. ✅ Backend health check passes
4. ✅ Frontend connects without errors
5. ✅ All database operations work

---

**Last Updated**: 2025-09-28  
**Status**: Complete solution for PGRST205 error  
**Tested**: ✅ Render deployment + Vercel frontend
