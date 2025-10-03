#!/usr/bin/env python3
"""
Quick SendGrid Setup for Render - MediCare+ Platform
Get SendGrid working in 5 minutes
"""

def show_quick_sendgrid_setup():
    """Show quick SendGrid setup guide"""
    print("⚡ QUICK SENDGRID SETUP FOR RENDER - 5 MINUTES")
    print("="*80)
    print()
    print("🎯 GOAL: Get emails actually delivered to Gmail inbox")
    print("❌ CURRENT: Emails stored locally (not sent)")
    print("✅ SOLUTION: Configure SendGrid API")
    print()
    
    print("="*80)
    print("📋 STEP-BY-STEP SETUP")
    print("="*80)
    print()
    
    print("🔥 STEP 1: Create SendGrid Account (2 minutes)")
    print("-" * 50)
    print("1. Go to: https://sendgrid.com")
    print("2. Click 'Start for Free'")
    print("3. Sign up with your email")
    print("4. Verify your email address")
    print("5. Complete the setup wizard")
    print()
    
    print("🔑 STEP 2: Get API Key (1 minute)")
    print("-" * 50)
    print("1. In SendGrid dashboard, go to 'Settings' → 'API Keys'")
    print("2. Click 'Create API Key'")
    print("3. Name it: 'MediCare-Render'")
    print("4. Select 'Restricted Access'")
    print("5. Under 'Mail Send', select 'Full Access'")
    print("6. Click 'Create & View'")
    print("7. COPY the API key (starts with 'SG.')")
    print("   Example: SG.abc123def456...")
    print()
    
    print("🚀 STEP 3: Configure Render (1 minute)")
    print("-" * 50)
    print("1. Go to your Render dashboard")
    print("2. Select your MediCare+ backend service")
    print("3. Click 'Environment' tab")
    print("4. Click 'Add Environment Variable'")
    print("5. Set:")
    print("   Key: SENDGRID_API_KEY")
    print("   Value: [paste your API key here]")
    print("6. Click 'Save Changes'")
    print("7. Wait for automatic redeploy (2-3 minutes)")
    print()
    
    print("✅ STEP 4: Test Email (1 minute)")
    print("-" * 50)
    print("1. Go to your MediCare+ frontend")
    print("2. Make a prediction")
    print("3. Enter email: gowthaamaneswar1998@gmail.com")
    print("4. Click 'Email Report'")
    print("5. Should see: '✅ Email sent successfully via SendGrid'")
    print("6. Check Gmail inbox (and spam folder)")
    print()
    
    print("="*80)
    print("🔍 VERIFICATION CHECKLIST")
    print("="*80)
    print()
    print("After setup, check these:")
    print("✅ Render logs show: 'Available Providers: [SendGrid]'")
    print("✅ Frontend shows: 'Email sent successfully via SendGrid'")
    print("✅ Gmail inbox receives MediCare+ report")
    print("✅ No more 'stored locally' messages")
    print()
    
    print("="*80)
    print("🆘 TROUBLESHOOTING")
    print("="*80)
    print()
    print("If emails still don't work:")
    print()
    print("1. Check Render service logs:")
    print("   - Look for 'SendGrid' in available providers")
    print("   - Check for API key errors")
    print()
    print("2. Verify SendGrid API key:")
    print("   - Must start with 'SG.'")
    print("   - Must have 'Mail Send' permissions")
    print("   - Copy/paste carefully (no extra spaces)")
    print()
    print("3. Check SendGrid dashboard:")
    print("   - Go to Activity → Email Activity")
    print("   - Look for sent emails")
    print("   - Check for delivery status")
    print()
    print("4. Gmail delivery issues:")
    print("   - Check spam/junk folder")
    print("   - Add noreply@sendgrid.net to contacts")
    print("   - Wait 5-10 minutes for delivery")
    print()
    
    print("="*80)
    print("💡 ALTERNATIVE: MAILGUN SETUP")
    print("="*80)
    print()
    print("If SendGrid doesn't work, try Mailgun:")
    print("1. Go to: https://mailgun.com")
    print("2. Sign up for free account")
    print("3. Get API key from dashboard")
    print("4. In Render, set environment variables:")
    print("   MAILGUN_API_KEY=your_api_key")
    print("   MAILGUN_DOMAIN=sandbox-xxx.mailgun.org")
    print()
    
    print("="*80)
    print("🎉 SUCCESS INDICATORS")
    print("="*80)
    print()
    print("When working correctly, you'll see:")
    print("📱 Frontend: '✅ Email sent successfully via SendGrid to gowthaamaneswar1998@gmail.com!'")
    print("📧 Gmail: Professional MediCare+ insurance report")
    print("📊 Render logs: 'Email sent via SendGrid in X.Xs'")
    print("📈 SendGrid dashboard: Email activity showing delivered emails")
    print()
    print("🚀 TOTAL SETUP TIME: ~5 minutes")
    print("💰 COST: FREE (100 emails/day)")
    print("✅ RELIABILITY: High (99.9% delivery rate)")

def show_current_status():
    """Show current email service status"""
    print("\n" + "="*80)
    print("📊 CURRENT EMAIL SERVICE STATUS")
    print("="*80)
    
    import os
    
    # Check environment variables
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    mailgun_key = os.getenv("MAILGUN_API_KEY")
    
    print(f"SendGrid API Key: {'✅ SET' if sendgrid_key else '❌ NOT SET'}")
    if sendgrid_key:
        print(f"   Value: {sendgrid_key[:10]}..." if len(sendgrid_key) > 10 else f"   Value: {sendgrid_key}")
    
    print(f"Mailgun API Key: {'✅ SET' if mailgun_key else '❌ NOT SET'}")
    if mailgun_key:
        print(f"   Value: {mailgun_key[:10]}..." if len(mailgun_key) > 10 else f"   Value: {mailgun_key}")
    
    if not sendgrid_key and not mailgun_key:
        print("\n❌ NO EMAIL PROVIDERS CONFIGURED")
        print("💡 This is why emails are 'stored locally' instead of sent")
        print("🔧 Follow the setup guide above to fix this")
    else:
        print("\n✅ EMAIL PROVIDER CONFIGURED")
        print("🎉 Emails should be delivered to Gmail inbox")

if __name__ == "__main__":
    show_quick_sendgrid_setup()
    show_current_status()
