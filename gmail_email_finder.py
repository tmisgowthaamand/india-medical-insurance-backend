#!/usr/bin/env python3
"""
Gmail Email Finder - MediCare+ Platform
Help users find MediCare+ emails in their Gmail inbox
"""

def show_gmail_search_guide():
    """Show comprehensive guide to find MediCare+ emails"""
    print("🔍 GMAIL EMAIL FINDER - MediCare+ Platform")
    print("="*80)
    print()
    print("📧 LOOKING FOR: MediCare+ Insurance Report emails")
    print("📨 SENT TO: gowthaamaneswar1998@gmail.com")
    print()
    
    print("="*80)
    print("🎯 GMAIL SEARCH COMMANDS")
    print("="*80)
    print()
    print("Copy and paste these into Gmail search box:")
    print()
    print("1️⃣ Search by sender:")
    print("   from:gokrishna98@gmail.com")
    print()
    print("2️⃣ Search by subject:")
    print("   subject:MediCare+")
    print()
    print("3️⃣ Search by content:")
    print("   MediCare+ Insurance Report")
    print()
    print("4️⃣ Search by amount:")
    print("   ₹17,823 OR ₹15,122 OR ₹21,996")
    print()
    print("5️⃣ Search recent emails:")
    print("   MediCare+ newer_than:1d")
    print()
    
    print("="*80)
    print("📂 CHECK THESE GMAIL FOLDERS")
    print("="*80)
    print()
    print("✅ Primary Inbox")
    print("   - Main inbox tab")
    print("   - Look for 'MediCare+ Platform' sender")
    print()
    print("📢 Promotions Tab")
    print("   - Click 'Promotions' tab in Gmail")
    print("   - Marketing emails often go here")
    print()
    print("🗑️ Spam/Junk Folder")
    print("   - Click 'Spam' in left sidebar")
    print("   - New senders often get filtered here")
    print()
    print("📋 All Mail")
    print("   - Click 'All Mail' in left sidebar")
    print("   - Shows ALL emails regardless of folder")
    print()
    
    print("="*80)
    print("🔍 WHAT TO LOOK FOR")
    print("="*80)
    print()
    print("📧 Email Subject:")
    print("   🏥 MediCare+ Insurance Report - ₹XX,XXX")
    print()
    print("👤 Sender Name:")
    print("   MediCare+ Platform")
    print("   MediCare+ Insurance Platform")
    print()
    print("📨 Sender Email:")
    print("   gokrishna98@gmail.com")
    print("   noreply@sendgrid.net (if using SendGrid)")
    print("   noreply@mailgun.org (if using Mailgun)")
    print()
    print("💰 Content Keywords:")
    print("   - Insurance Report")
    print("   - Prediction Report")
    print("   - AI-Powered Analysis")
    print("   - Patient Details")
    print("   - ₹ (Rupee symbol)")
    print()
    
    print("="*80)
    print("⏰ EMAIL DELIVERY TIMELINE")
    print("="*80)
    print()
    print("📅 When emails are sent:")
    print("   - Immediately after clicking 'Email Report'")
    print("   - Frontend shows: '✅ Email sent successfully'")
    print()
    print("⏱️ Delivery time:")
    print("   - SendGrid: 1-5 minutes")
    print("   - Mailgun: 1-10 minutes")
    print("   - Local Storage: Never delivered (stored locally)")
    print()
    print("🕐 Check timeline:")
    print("   - Immediate: Check sent confirmation")
    print("   - 2 minutes: Check primary inbox")
    print("   - 5 minutes: Check promotions tab")
    print("   - 10 minutes: Check spam folder")
    print("   - 15 minutes: Check all mail")
    print()
    
    print("="*80)
    print("🚨 TROUBLESHOOTING STEPS")
    print("="*80)
    print()
    print("❌ If emails are not found:")
    print()
    print("1️⃣ Verify email address:")
    print("   - Check spelling: gowthaamaneswar1998@gmail.com")
    print("   - No typos in email input")
    print()
    print("2️⃣ Check email service status:")
    print("   - Frontend shows 'stored locally' = not delivered")
    print("   - Frontend shows 'via SendGrid' = should be delivered")
    print()
    print("3️⃣ Gmail settings:")
    print("   - Check Gmail filters (Settings → Filters)")
    print("   - Check blocked senders")
    print("   - Disable aggressive spam filtering")
    print()
    print("4️⃣ Add to contacts:")
    print("   - Add gokrishna98@gmail.com to contacts")
    print("   - This prevents future emails going to spam")
    print()
    print("5️⃣ Check other email accounts:")
    print("   - Verify you're checking the correct Gmail account")
    print("   - Log out and log back into Gmail")
    print()
    
    print("="*80)
    print("✅ SUCCESS INDICATORS")
    print("="*80)
    print()
    print("When emails are working correctly:")
    print()
    print("📱 Frontend message:")
    print("   '✅ Email sent successfully via SendGrid to gowthaamaneswar1998@gmail.com!'")
    print()
    print("📧 Gmail inbox:")
    print("   - Professional MediCare+ report")
    print("   - Prediction amount (₹XX,XXX)")
    print("   - Patient details table")
    print("   - MediCare+ branding")
    print()
    print("⏰ Timing:")
    print("   - Email arrives within 5 minutes")
    print("   - Consistent delivery for each report")
    print()
    
    print("="*80)
    print("🎯 CURRENT STATUS CHECK")
    print("="*80)
    
    # Show current email status from logs
    import os
    
    # Check if we have stored emails
    if os.path.exists("user_emails.json"):
        try:
            import json
            with open("user_emails.json", 'r') as f:
                user_emails = json.load(f)
                print("📁 Stored user emails found:")
                for user_id, data in user_emails.items():
                    emails = data.get('emails', [])
                    print(f"   User {user_id}: {emails}")
        except:
            print("📁 User emails file exists but couldn't read")
    else:
        print("📁 No stored user emails found")
    
    # Check if we have pending emails
    if os.path.exists("pending_emails.json"):
        try:
            import json
            with open("pending_emails.json", 'r') as f:
                pending = json.load(f)
                print(f"📋 Pending emails: {len(pending)} emails waiting")
                if pending:
                    latest = pending[-1]
                    print(f"   Latest: {latest['recipient']} at {latest['timestamp']}")
        except:
            print("📋 Pending emails file exists but couldn't read")
    else:
        print("📋 No pending emails found")
    
    print("\n💡 RECOMMENDATION:")
    if os.path.exists("pending_emails.json"):
        print("❌ Emails are being stored locally (not delivered)")
        print("🔧 Configure SendGrid API key in Render to enable delivery")
    else:
        print("✅ Email system appears to be working")
        print("📧 Check Gmail inbox using search methods above")

if __name__ == "__main__":
    show_gmail_search_guide()
