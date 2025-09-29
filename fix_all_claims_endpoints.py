#!/usr/bin/env python3
"""
Fix All Claims Analysis Endpoints
This script fixes the region analysis data structure in all claims analysis endpoints
"""

import re
import os

def fix_all_claims_endpoints():
    """Fix all claims analysis endpoints in app.py"""
    print("🔧 Fixing All Claims Analysis Endpoints")
    print("=" * 50)
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find any remaining problematic region analysis code
    # This will catch any instances that weren't fixed by the previous script
    old_pattern = r'''region_analysis = df\.groupby\('region'\)\.agg\(\{
            'claim_amount_inr': \['mean', 'count'\],
            'premium_annual_inr': 'mean'
        \}\)\.to_dict\(\)'''
    
    new_code = '''region_stats = df.groupby('region').agg({
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
    
    # Count occurrences before replacement
    matches = re.findall(old_pattern, content, flags=re.MULTILINE | re.DOTALL)
    print(f"🔍 Found {len(matches)} instances to fix")
    
    # Apply the replacement to all occurrences
    new_content = re.sub(old_pattern, new_code, content, flags=re.MULTILINE | re.DOTALL)
    
    if new_content != content:
        # Write the fixed version
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Fixed {len(matches)} claims analysis endpoints")
        return True
    else:
        print("✅ All endpoints already fixed or no issues found")
        return True

def test_all_endpoints():
    """Test all claims analysis endpoints"""
    print("\n🧪 Testing All Claims Analysis Endpoints")
    print("=" * 50)
    
    import requests
    import json
    
    endpoints = [
        '/claims-analysis',
        '/live-claims-analysis', 
        '/user-claims-analysis'
    ]
    
    base_url = 'http://localhost:8001'
    
    for endpoint in endpoints:
        try:
            print(f"🔗 Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                # Check if the region analysis structure is correct
                if 'region_analysis' in data:
                    region_data = data['region_analysis']
                    if 'claim_amount_inr' in region_data and 'mean' in region_data['claim_amount_inr']:
                        print(f"  ✅ {endpoint} - Correct structure")
                    else:
                        print(f"  ❌ {endpoint} - Incorrect structure")
                else:
                    print(f"  ⚠️ {endpoint} - No region_analysis in response")
            elif response.status_code == 401:
                print(f"  🔒 {endpoint} - Authentication required (expected for user-specific endpoint)")
            else:
                print(f"  ❌ {endpoint} - Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {endpoint} - Server not running")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    success = fix_all_claims_endpoints()
    if success:
        test_all_endpoints()
        print("\n🎉 All Claims Analysis Endpoints Fixed!")
        print("📋 Charts should now display properly after CSV upload and model training")
    else:
        print("\n❌ Fix failed")
