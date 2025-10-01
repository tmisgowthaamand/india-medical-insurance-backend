
# Render Deployment Checklist for Email Fix

## ✅ Pre-deployment Checklist

### 1. Code Changes Applied
- [x] Updated app.py email endpoint logic
- [x] Updated database.py email saving logic  
- [x] Email service handles existing emails properly
- [x] All fixes tested on localhost

### 2. Environment Variables Required
Add these to Render Dashboard > Environment:

```
GMAIL_EMAIL=gokrishna98@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password
SUPABASE_URL=https://gucyzhjyciqnvxedmoxo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

### 3. Gmail App Password Setup
- [ ] Enable 2-Factor Authentication on Gmail
- [ ] Generate App Password: Google Account > Security > 2-Step Verification > App passwords
- [ ] Use 16-character password (no spaces)

## 🚀 Deployment Steps

### 1. Update Environment Variables
- [ ] Go to Render Dashboard
- [ ] Select backend service (srv-d3b668ogjchc73f9ece0)
- [ ] Navigate to Environment tab
- [ ] Add/update all required variables
- [ ] Save changes

### 2. Deploy Updated Code
- [ ] Push code changes to GitHub repository
- [ ] Render will auto-deploy from GitHub
- [ ] Wait for deployment to complete (5-10 minutes)

### 3. Test Deployment
- [ ] Wait for service to start (may take 30-60 seconds)
- [ ] Test health endpoint: GET /health
- [ ] Test email endpoint with existing email: perivihk@gmail.com
- [ ] Verify email is sent successfully

## 🧪 Testing Commands

### Test Render Backend
```bash
curl https://srv-d3b668ogjchc73f9ece0.onrender.com/health
```

### Test Email Functionality
```bash
curl -X POST https://srv-d3b668ogjchc73f9ece0.onrender.com/send-prediction-email   -H "Content-Type: application/json"   -d '{
    "email": "perivihk@gmail.com",
    "prediction": {"prediction": 25000.0, "confidence": 0.85},
    "patient_data": {
      "age": 35, "bmi": 23.0, "gender": "Male", 
      "smoker": "No", "region": "East", "premium_annual_inr": 30000
    }
  }'
```

## 🔧 Troubleshooting

### If Email Fails:
1. Check Render logs for error messages
2. Verify Gmail App Password is correct
3. Ensure all environment variables are set
4. Check Supabase connection

### If Service Won't Start:
1. Check Render build logs
2. Verify all dependencies in requirements.txt
3. Check for Python syntax errors
4. Ensure all imports are available

### If Database Errors:
1. Verify Supabase URL and key
2. Check database tables exist
3. Run database migration if needed

## ✅ Success Criteria

- [ ] Render service starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] Email endpoint accepts existing emails (perivihk@gmail.com)
- [ ] Emails are sent successfully
- [ ] No "email already exists" blocking issues
- [ ] Frontend can send emails through Render backend

## 📞 Support

If issues persist:
1. Check Render service logs
2. Verify environment variables
3. Test with fresh email address
4. Check Gmail account settings
