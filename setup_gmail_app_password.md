# Gmail App Password Setup Guide

## Steps to Generate Gmail App Password for gokrishna98@gmail.com

### 1. Enable 2-Factor Authentication (if not already enabled)
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Sign in with `gokrishna98@gmail.com`
3. Under "Signing in to Google", click "2-Step Verification"
4. Follow the setup process if not already enabled

### 2. Generate App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Sign in with `gokrishna98@gmail.com`
3. Select "Mail" from the dropdown
4. Select "Other (Custom name)" and enter: `MediCare+ Platform`
5. Click "Generate"
6. Copy the 16-character app password (format: xxxx xxxx xxxx xxxx)

### 3. Update .env File
Replace `your-gmail-app-password-here` in the .env file with the generated app password:
```
GMAIL_EMAIL=gokrishna98@gmail.com
GMAIL_APP_PASSWORD=your-generated-16-char-password
```

### 4. Test Email Functionality
After updating the .env file:
1. Restart the backend server
2. Try sending an email from the prediction form
3. Check your Gmail inbox for the prediction report

## Troubleshooting
- Make sure 2FA is enabled on your Google account
- Use the app password, not your regular Gmail password
- Remove any spaces from the app password when copying to .env
- Restart the backend server after updating .env

## Security Note
- Keep your app password secure
- Don't share it publicly
- You can revoke it anytime from Google Account settings
