#!/usr/bin/env python3
"""
Debug Server for MediCare+ Backend
This script helps diagnose 500 errors and server issues
"""

import os
import sys
import traceback
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check all required environment variables"""
    logger.info("🔍 Checking Environment Variables...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY",
        "JWT_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            logger.error(f"❌ Missing: {var}")
        else:
            logger.info(f"✅ Found: {var} = {value[:20]}..." if len(value) > 20 else f"✅ Found: {var} = {value}")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All environment variables found")
    return True

def check_database_connection():
    """Test database connection"""
    logger.info("🔍 Testing Database Connection...")
    
    try:
        from database import supabase_client
        
        if not supabase_client.is_enabled():
            logger.error("❌ Supabase client not enabled")
            return False
        
        # Test a simple query
        result = supabase_client.client.table("users").select("*").limit(1).execute()
        logger.info("✅ Database connection successful")
        logger.info(f"📊 Users table accessible, found {len(result.data)} records")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error(f"Full error: {traceback.format_exc()}")
        return False

def check_model_files():
    """Check if model files exist"""
    logger.info("🔍 Checking Model Files...")
    
    model_path = "models/model_pipeline.pkl"
    metadata_path = "models/training_metadata.json"
    
    if os.path.exists(model_path):
        logger.info(f"✅ Model file found: {model_path}")
        logger.info(f"📁 File size: {os.path.getsize(model_path)} bytes")
    else:
        logger.warning(f"⚠️ Model file not found: {model_path}")
    
    if os.path.exists(metadata_path):
        logger.info(f"✅ Metadata file found: {metadata_path}")
    else:
        logger.warning(f"⚠️ Metadata file not found: {metadata_path}")

def check_data_files():
    """Check if data files exist"""
    logger.info("🔍 Checking Data Files...")
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        logger.warning(f"⚠️ Data directory not found: {data_dir}")
        return
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if csv_files:
        logger.info(f"✅ Found {len(csv_files)} CSV files: {csv_files}")
    else:
        logger.warning("⚠️ No CSV files found in data directory")

def test_imports():
    """Test all critical imports"""
    logger.info("🔍 Testing Critical Imports...")
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("supabase", "create_client"),
        ("pandas", "pd"),
        ("numpy", "np"),
        ("joblib", "load"),
        ("model_pipeline", "build_pipeline"),
        ("utils", "hash_password"),
        ("database", "supabase_client")
    ]
    
    failed_imports = []
    
    for module_name, import_item in imports_to_test:
        try:
            if module_name == "pandas":
                import pandas as pd
            elif module_name == "numpy":
                import numpy as np
            elif module_name == "joblib":
                from joblib import load
            elif module_name == "fastapi":
                from fastapi import FastAPI
            elif module_name == "supabase":
                from supabase import create_client
            elif module_name == "model_pipeline":
                from model_pipeline import build_pipeline
            elif module_name == "utils":
                from utils import hash_password
            elif module_name == "database":
                from database import supabase_client
            
            logger.info(f"✅ Import successful: {module_name}")
        except Exception as e:
            logger.error(f"❌ Import failed: {module_name} - {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        logger.error(f"❌ Failed imports: {failed_imports}")
        return False
    
    logger.info("✅ All imports successful")
    return True

def test_server_startup():
    """Test server startup process"""
    logger.info("🔍 Testing Server Startup...")
    
    try:
        # Import and test app creation
        from app import app
        logger.info("✅ FastAPI app created successfully")
        
        # Test startup event
        import asyncio
        from app import startup_event
        
        # Run startup event
        asyncio.run(startup_event())
        logger.info("✅ Startup event completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        logger.error(f"Full error: {traceback.format_exc()}")
        return False

def run_diagnostics():
    """Run all diagnostic tests"""
    logger.info("🏥 MediCare+ Backend Diagnostics")
    logger.info("=" * 50)
    
    tests = [
        ("Environment Variables", check_environment),
        ("Critical Imports", test_imports),
        ("Data Files", check_data_files),
        ("Model Files", check_model_files),
        ("Database Connection", check_database_connection),
        ("Server Startup", test_server_startup)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 DIAGNOSTIC SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All diagnostics passed! Your server should work.")
    else:
        logger.error("⚠️ Some diagnostics failed. Check the errors above.")
        
        # Provide specific recommendations
        logger.info("\n🔧 RECOMMENDATIONS:")
        
        if not results.get("Environment Variables"):
            logger.info("1. Check your .env file has all required variables")
            logger.info("2. Make sure SUPABASE_URL and keys are correct")
        
        if not results.get("Database Connection"):
            logger.info("3. Run the database table creation script")
            logger.info("4. Verify your Supabase project is active")
        
        if not results.get("Critical Imports"):
            logger.info("5. Install missing Python packages: pip install -r requirements.txt")
        
        if not results.get("Server Startup"):
            logger.info("6. Check the full error logs above for specific issues")

if __name__ == "__main__":
    run_diagnostics()
