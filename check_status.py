#!/usr/bin/env python3
"""
Quick status check for Supabase integration
"""

from database import supabase_client

def check_status():
    """Check current status of Supabase integration"""
    
    print("🔍 Checking Supabase Integration Status...")
    
    if not supabase_client.is_enabled():
        print("❌ Supabase not enabled")
        return
    
    try:
        # Check model metadata
        result = supabase_client.client.table('model_metadata').select('*').order('created_at', desc=True).limit(5).execute()
        
        print(f"📊 Found {len(result.data)} models in database:")
        for i, model in enumerate(result.data[:3], 1):
            version = model.get('model_version', 'Unknown')
            samples = model.get('training_samples', 'Unknown')
            r2 = model.get('test_r2', 'Unknown')
            print(f"   {i}. Model v{version} | Samples: {samples} | R²: {r2}")
        
        # Check datasets
        datasets_result = supabase_client.client.table('datasets').select('*').limit(5).execute()
        print(f"📁 Found {len(datasets_result.data)} datasets")
        
        print("\n✅ Supabase integration is working correctly!")
        print("🚀 Ready for upload testing!")
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    check_status()
