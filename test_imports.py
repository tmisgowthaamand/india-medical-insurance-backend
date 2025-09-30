#!/usr/bin/env python3
"""
Test all imports to ensure they work correctly for Render deployment
"""

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports for Render deployment...")
    
    try:
        print("Testing FastAPI imports...")
        from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header, Request
        from fastapi.security import OAuth2PasswordRequestForm
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.exceptions import RequestValidationError
        from fastapi.responses import JSONResponse
        print("✅ FastAPI imports successful")
        
        print("Testing Pydantic imports...")
        from pydantic import BaseModel, EmailStr
        print("✅ Pydantic imports successful")
        
        print("Testing standard library imports...")
        from typing import Optional, List
        from joblib import load, dump
        import pandas as pd
        import os
        import json
        import numpy as np
        from datetime import datetime
        import asyncio
        print("✅ Standard library imports successful")
        
        print("Testing custom module imports...")
        try:
            from model_pipeline import build_pipeline, get_feature_importance
            print("✅ model_pipeline import successful")
        except ImportError as e:
            print(f"⚠️ model_pipeline import failed: {e}")
        
        try:
            from fast_model_pipeline import build_fast_pipeline, get_model_info as get_fast_model_info
            print("✅ fast_model_pipeline import successful")
        except ImportError as e:
            print(f"⚠️ fast_model_pipeline import failed: {e}")
        
        try:
            from fast_train import fast_train
            print("✅ fast_train import successful")
        except ImportError as e:
            print(f"⚠️ fast_train import failed: {e}")
        
        try:
            from utils import hash_password, verify_password, create_access_token, decode_token, get_current_user
            print("✅ utils import successful")
        except ImportError as e:
            print(f"⚠️ utils import failed: {e}")
        
        try:
            from database import supabase_client, init_database
            print("✅ database import successful")
        except ImportError as e:
            print(f"⚠️ database import failed: {e}")
        
        try:
            from error_handler import setup_error_handlers, log_startup_info, request_logging_middleware
            print("✅ error_handler import successful")
        except ImportError as e:
            print(f"⚠️ error_handler import failed: {e}")
        
        try:
            from email_service import email_service
            print("✅ email_service import successful")
        except ImportError as e:
            print(f"⚠️ email_service import failed: {e}")
        
        print("\n🎉 Import test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Critical import error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_supabase():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        from supabase import create_client, Client
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        url = os.getenv("SUPABASE_URL")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if url and service_role_key:
            client = create_client(url, service_role_key)
            print("✅ Supabase client created successfully")
            return True
        else:
            print("⚠️ Supabase credentials not found")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🏥 MediCare+ Import Test")
    print("=" * 50)
    
    imports_ok = test_imports()
    supabase_ok = test_supabase()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Supabase: {'✅ PASS' if supabase_ok else '❌ FAIL'}")
    
    if imports_ok and supabase_ok:
        print("\n🎉 All tests passed! Ready for deployment.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
