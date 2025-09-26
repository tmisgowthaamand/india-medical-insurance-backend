# Backend Environment Variables for Deployment

## 🔧 Environment Variables Setup

When deploying to Render, you'll need to set these environment variables in your Render service dashboard:

### ✅ Required Environment Variables

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `SUPABASE_URL` | `https://gucyzhjyciqnvxedmoxo.supabase.co` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODA0MTksImV4cCI6MjA3NDQ1NjQxOX0.BYbV3CHVTrd4KzhRAFSYB7S2RiFv342f0J-Es-4pkKI` | Your Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1Y3l6aGp5Y2lxbnZ4ZWRtb3hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODg4MDQxOSwiZXhwIjoyMDc0NDU2NDE5fQ.yBrXifdpZ9vrymLQ1EiZnspxHfF0x73wAP0Mfl96kk4` | Your Supabase service role key (admin access) |
| `JWT_SECRET_KEY` | `medical_insurance_dashboard_jwt_secret_key_2024_change_in_production` | Change this to a stronger key in production |
| `ALLOWED_ORIGINS` | `https://your-frontend-domain.vercel.app` | Your Vercel frontend URL |
| `ENVIRONMENT` | `production` | Set to production for deployment |

### 🔒 Optional Configuration

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `JWT_ALGORITHM` | `HS256` | JWT algorithm (default) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |

## 🚀 How to Set in Render

1. Go to your Render service dashboard
2. Click on **Environment** tab
3. Add each variable:
   - Click **Add Environment Variable**
   - Enter the **Key** (variable name)
   - Enter the **Value**
   - Click **Save Changes**

## ⚠️ Security Notes

- **Never commit** the `.env` file to Git (it's in `.gitignore`)
- **Change JWT_SECRET_KEY** to a stronger, random key for production
- **Keep your Supabase keys secure** and don't share them publicly
- **Use HTTPS** for all production URLs

## 🔄 After Setting Variables

1. Your Render service will automatically redeploy
2. Check the logs to ensure no environment variable errors
3. Test your API endpoints to confirm everything works

## 🧪 Testing Your Setup

You can test your backend locally with these environment variables:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Then visit `http://localhost:8000/health` to check if everything is working.

## 📋 Deployment Checklist

- [ ] Supabase URL set correctly
- [ ] Supabase anon key set correctly
- [ ] JWT secret key set (change for production)
- [ ] CORS origins configured with frontend URL
- [ ] Environment set to "production"
- [ ] All variables saved in Render dashboard
- [ ] Service redeployed successfully
- [ ] Health check endpoint responding
