#!/usr/bin/env python3
"""
Test script to verify Supabase integration
"""
import asyncio
import pandas as pd
from database import supabase_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_supabase_integration():
    """Test all Supabase functionality"""
    print("🧪 Testing Supabase Integration")
    print("=" * 50)
    
    # Test 1: Check if Supabase is configured
    print("1. Checking Supabase configuration...")
    if supabase_client.is_enabled():
        print("   ✅ Supabase is configured and enabled")
        print(f"   📍 URL: {supabase_client.url}")
    else:
        print("   ❌ Supabase is not configured")
        print("   💡 Please check your .env file and Supabase credentials")
        return False
    
    # Test 2: Test user operations
    print("\n2. Testing user operations...")
    try:
        # Create test user
        test_email = "test@example.com"
        result = await supabase_client.create_user(test_email, "test123", False)
        
        if "error" in result:
            if "already exists" in str(result["error"]).lower():
                print("   ✅ User already exists (expected)")
            else:
                print(f"   ⚠️  User creation error: {result['error']}")
        else:
            print("   ✅ Test user created successfully")
        
        # Get user
        user = await supabase_client.get_user(test_email)
        if user:
            print("   ✅ User retrieval successful")
        else:
            print("   ❌ User retrieval failed")
            
    except Exception as e:
        print(f"   ❌ User operations failed: {e}")
    
    # Test 3: Test dataset operations
    print("\n3. Testing dataset operations...")
    try:
        # Create sample dataset
        sample_data = pd.DataFrame({
            'age': [25, 30, 35, 40],
            'bmi': [22.5, 25.0, 27.5, 30.0],
            'gender': ['Male', 'Female', 'Male', 'Female'],
            'smoker': ['No', 'Yes', 'No', 'Yes'],
            'region': ['North', 'South', 'East', 'West'],
            'premium_annual_inr': [15000, 20000, 18000, 25000],
            'claim_amount_inr': [5000, 8000, 6000, 12000]
        })
        
        # Store dataset
        result = await supabase_client.store_dataset("test_dataset.csv", sample_data, {"test": True})
        
        if "error" in result:
            print(f"   ❌ Dataset storage failed: {result['error']}")
        else:
            print("   ✅ Dataset stored successfully")
            dataset_id = result.get("dataset_id")
            
            # Retrieve dataset
            retrieved_df = await supabase_client.get_dataset(dataset_id=dataset_id)
            if retrieved_df is not None and len(retrieved_df) == len(sample_data):
                print("   ✅ Dataset retrieval successful")
            else:
                print("   ❌ Dataset retrieval failed or data mismatch")
                
    except Exception as e:
        print(f"   ❌ Dataset operations failed: {e}")
    
    # Test 4: Test prediction storage
    print("\n4. Testing prediction storage...")
    try:
        input_data = {
            'age': 30,
            'bmi': 25.0,
            'gender': 'Male',
            'smoker': 'No',
            'region': 'North',
            'premium_annual_inr': 18000
        }
        
        result = await supabase_client.store_prediction(
            user_email="test@example.com",
            input_data=input_data,
            prediction=7500.0,
            confidence=0.85
        )
        
        if "error" in result:
            print(f"   ❌ Prediction storage failed: {result['error']}")
        else:
            print("   ✅ Prediction stored successfully")
            
            # Get user predictions
            predictions = await supabase_client.get_user_predictions("test@example.com", limit=5)
            if predictions:
                print(f"   ✅ Retrieved {len(predictions)} predictions for user")
            else:
                print("   ⚠️  No predictions found for user")
                
    except Exception as e:
        print(f"   ❌ Prediction operations failed: {e}")
    
    # Test 5: Test model metadata
    print("\n5. Testing model metadata...")
    try:
        model_info = {
            'training_date': '2024-01-01T00:00:00',
            'training_samples': 80,
            'test_samples': 20,
            'train_rmse': 2500.0,
            'test_rmse': 3000.0,
            'train_r2': 0.95,
            'test_r2': 0.85,
            'features': ['age', 'bmi', 'gender', 'smoker', 'region', 'premium_annual_inr']
        }
        
        result = await supabase_client.store_model_metadata(model_info)
        
        if "error" in result:
            print(f"   ❌ Model metadata storage failed: {result['error']}")
        else:
            print("   ✅ Model metadata stored successfully")
            
            # Get latest model metadata
            latest_model = await supabase_client.get_latest_model_metadata()
            if latest_model:
                print("   ✅ Model metadata retrieval successful")
            else:
                print("   ❌ Model metadata retrieval failed")
                
    except Exception as e:
        print(f"   ❌ Model metadata operations failed: {e}")
    
    # Test 6: Test dataset listing
    print("\n6. Testing dataset listing...")
    try:
        datasets = await supabase_client.list_datasets()
        print(f"   ✅ Found {len(datasets)} datasets in database")
        
        if datasets:
            latest_dataset = datasets[0]
            print(f"   📊 Latest dataset: {latest_dataset.get('filename')} ({latest_dataset.get('rows')} rows)")
            
    except Exception as e:
        print(f"   ❌ Dataset listing failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Supabase integration test completed!")
    print("\nNext steps:")
    print("1. Update your .env files with actual Supabase credentials")
    print("2. Run the SQL schema in your Supabase dashboard")
    print("3. Test the full application with frontend and backend")
    
    return True

async def test_environment_variables():
    """Test if environment variables are properly set"""
    print("🔧 Testing Environment Variables")
    print("=" * 30)
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value in ['your_supabase_project_url', 'your_anon_key_here', 'your_service_role_key_here']:
            placeholder_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * 10}...{value[-10:]}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    
    if placeholder_vars:
        print(f"⚠️  Placeholder values detected: {', '.join(placeholder_vars)}")
        print("   Please update these with your actual Supabase credentials")
    
    if not missing_vars and not placeholder_vars:
        print("✅ All environment variables are properly configured")
        return True
    
    return False

if __name__ == "__main__":
    print("🚀 Starting Supabase Integration Tests\n")
    print("Your Supabase Organization: ulvqxgvdoggtszgbdzoh")
    print("Dashboard: https://supabase.com/dashboard/org/ulvqxgvdoggtszgbdzoh")
    print()
    
    # Test environment variables first
    env_ok = asyncio.run(test_environment_variables())
    
    if env_ok:
        # Run integration tests
        asyncio.run(test_supabase_integration())
    else:
        print("\n❌ Please fix environment variables before running integration tests")
        print("💡 Quick setup options:")
        print("   1. Run: python ../setup_supabase.py (interactive setup)")
        print("   2. Check: YOUR_SUPABASE_SETUP.md (detailed guide)")
        print("   3. Manual: Update .env files with your Supabase credentials")
