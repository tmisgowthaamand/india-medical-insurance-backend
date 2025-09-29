#!/usr/bin/env python3
"""
Apply Claims Analysis Fix to app.py
This script applies the region analysis data structure fix
"""

import re
import os

def apply_claims_fix():
    """Apply the claims analysis fix to app.py"""
    print("🔧 Applying Claims Analysis Fix to app.py")
    print("=" * 50)
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic region analysis code
    # Look for the specific pattern in the get_claims_analysis function
    old_pattern = r'''        # Region analysis
        region_analysis = df\.groupby\('region'\)\.agg\(\{
            'claim_amount_inr': \['mean', 'count'\],
            'premium_annual_inr': 'mean'
        \}\)\.to_dict\(\)'''
    
    new_code = '''        # Region analysis
        region_stats = df.groupby('region').agg({
            'claim_amount_inr': ['mean', 'count'],
            'premium_annual_inr': 'mean'
        })
        
        # Restructure region analysis to match frontend expectations
        region_analysis = {
            'claim_amount_inr': {
                'mean': region_stats[('claim_amount_inr', 'mean')].to_dict(),
                'count': region_stats[('claim_amount_inr', 'count')].to_dict()
            },
            'premium_annual_inr': region_stats[('premium_annual_inr', 'mean')].to_dict()
        }'''
    
    # Apply the replacement
    new_content = re.sub(old_pattern, new_code, content, flags=re.MULTILINE | re.DOTALL)
    
    if new_content != content:
        # Create backup
        with open('app_backup_before_claims_fix.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Created backup: app_backup_before_claims_fix.py")
        
        # Write the fixed version
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Applied claims analysis fix to app.py")
        
        return True
    else:
        print("⚠️ No changes made - pattern not found or already fixed")
        return False

def verify_fix():
    """Verify the fix was applied correctly"""
    print("\n🧪 Verifying Fix...")
    print("=" * 50)
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the new structure is present
    if "region_stats[('claim_amount_inr', 'mean')].to_dict()" in content:
        print("✅ Fix verified: New region analysis structure found")
        return True
    else:
        print("❌ Fix verification failed: New structure not found")
        return False

if __name__ == "__main__":
    success = apply_claims_fix()
    if success:
        if verify_fix():
            print("\n🎉 Claims Analysis Fix Applied Successfully!")
            print("📋 The charts should now display properly after CSV upload")
        else:
            print("\n❌ Fix verification failed")
    else:
        print("\n⚠️ Fix not applied - manual intervention may be needed")
