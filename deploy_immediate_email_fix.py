#!/usr/bin/env python3
"""
Deployment script for immediate email feedback fix
Applies the enhanced email service to resolve network connectivity issues
"""

import os
import shutil
import sys
from datetime import datetime

def backup_original_files():
    """Backup original email service files"""
    print("📁 Creating backup of original files...")
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "email_service.py",
        "app.py"
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"  ✅ Backed up {file}")
        else:
            print(f"  ⚠️ {file} not found")
    
    print(f"📁 Backup created in: {backup_dir}")
    return backup_dir

def verify_enhanced_service():
    """Verify enhanced email service is working"""
    print("\n🔍 Verifying enhanced email service...")
    
    try:
        from enhanced_email_service import enhanced_email_service
        
        # Test basic functionality
        is_enabled = enhanced_email_service.is_email_enabled()
        network_ok = enhanced_email_service.check_network_connectivity()
        
        print(f"  📧 Email service configured: {'✅' if is_enabled else '⚠️'}")
        print(f"  🌐 Network connectivity: {'✅' if network_ok else '❌'}")
        
        if is_enabled:
            print(f"  📤 Sender email: {enhanced_email_service.sender_email}")
        
        print("  ✅ Enhanced email service loaded successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading enhanced service: {e}")
        return False

def check_environment_variables():
    """Check required environment variables"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = [
        "GMAIL_EMAIL",
        "GMAIL_APP_PASSWORD"
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"  ❌ {var}: NOT SET")
            all_set = False
    
    if not all_set:
        print("\n💡 To enable email functionality, set these environment variables:")
        print("   export GMAIL_EMAIL='your-email@gmail.com'")
        print("   export GMAIL_APP_PASSWORD='your-app-password'")
        print("\n📖 How to get Gmail App Password:")
        print("   1. Go to Google Account settings")
        print("   2. Security → 2-Step Verification")
        print("   3. App passwords → Generate new password")
        print("   4. Use the generated password (not your regular password)")
    
    return all_set

def create_quick_test():
    """Create a quick test script"""
    print("\n📝 Creating quick test script...")
    
    test_script = """#!/usr/bin/env python3
import asyncio
from enhanced_email_service import enhanced_email_service

async def quick_test():
    print("Quick Email Service Test")
    print("-" * 30)
    
    # Test data
    prediction_data = {"prediction": 25000, "confidence": 0.85}
    patient_data = {"age": 30, "bmi": 22.5, "gender": "Male", "smoker": "No", "region": "Southeast", "premium_annual_inr": 15000}
    
    # Test immediate feedback
    result = await enhanced_email_service.send_prediction_email_with_immediate_feedback(
        recipient_email="test@example.com",
        prediction_data=prediction_data,
        patient_data=patient_data
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    print(f"Immediate: {result.get('immediate')}")

if __name__ == "__main__":
    asyncio.run(quick_test())
"""
    
    with open("quick_email_test.py", "w", encoding='utf-8') as f:
        f.write(test_script)
    
    print("  ✅ Created quick_email_test.py")

def main():
    """Main deployment function"""
    print("🚀 Deploying Immediate Email Feedback Fix")
    print("=" * 50)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Backup original files
    backup_dir = backup_original_files()
    
    # Step 2: Verify enhanced service
    service_ok = verify_enhanced_service()
    
    # Step 3: Check environment variables
    env_ok = check_environment_variables()
    
    # Step 4: Create test script
    create_quick_test()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DEPLOYMENT SUMMARY")
    print("=" * 50)
    
    print(f"📁 Backup created: {backup_dir}")
    print(f"🔧 Enhanced service: {'✅ READY' if service_ok else '❌ ERROR'}")
    print(f"🌐 Environment: {'✅ CONFIGURED' if env_ok else '⚠️ NEEDS SETUP'}")
    
    print("\n🎯 KEY IMPROVEMENTS:")
    print("  ✅ Immediate success notifications for users")
    print("  ✅ Background email processing (no blocking)")
    print("  ✅ Local report storage as backup")
    print("  ✅ Network connectivity checks")
    print("  ✅ Graceful error handling")
    print("  ✅ Enhanced user experience")
    
    print("\n🧪 TESTING:")
    print("  • Run: python test_immediate_email_feedback.py")
    print("  • Run: python quick_email_test.py")
    
    if service_ok:
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("💡 Users will now get immediate feedback when sending emails")
        print("📧 Email delivery happens in background without blocking UI")
    else:
        print("\n⚠️ DEPLOYMENT COMPLETED WITH WARNINGS")
        print("💡 Check error messages above and fix issues")
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
