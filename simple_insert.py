#!/usr/bin/env python3
"""
Simple insert with basic columns only
"""

from database import supabase_client

def simple_insert():
    """Insert with minimal columns"""
    
    print("🔧 Trying simple insert...")
    
    try:
        # Try with just basic columns that should exist
        basic_data = {
            "training_date": "2025-01-01T00:00:00Z",
            "training_samples": 1000
        }
        
        print("📊 Inserting basic data...")
        result = supabase_client.client.table("model_metadata").insert(basic_data).execute()
        
        if result.data:
            print("✅ Basic insert successful!")
            print(f"Inserted: {result.data}")
        else:
            print("❌ Basic insert failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Try even simpler
        try:
            print("🔧 Trying with just ID...")
            empty_data = {}
            result2 = supabase_client.client.table("model_metadata").insert(empty_data).execute()
            
            if result2.data:
                print("✅ Empty insert worked!")
                print(f"Result: {result2.data}")
            else:
                print("❌ Empty insert failed")
                
        except Exception as e2:
            print(f"❌ Empty insert error: {e2}")

if __name__ == "__main__":
    simple_insert()
