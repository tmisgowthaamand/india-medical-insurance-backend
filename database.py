"""
Supabase Database Configuration and Client
"""
import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
import json
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase database client for the medical insurance dashboard"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([self.url, self.anon_key, self.service_role_key]):
            logger.warning("Supabase credentials not found. Using fallback mode.")
            self.client = None
            self.enabled = False
        else:
            try:
                # Use the most compatible method - simple positional parameters
                self.client: Client = create_client(self.url, self.service_role_key)
                
                self.enabled = True
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                logger.error(f"URL: {self.url[:50] if self.url else 'None'}... (truncated)")
                logger.error(f"Key length: {len(self.service_role_key) if self.service_role_key else 0}")
                # Try to initialize without Supabase for fallback mode
                self.client = None
                self.enabled = False
                logger.warning("Falling back to local file storage mode")
    
    def is_enabled(self) -> bool:
        """Check if Supabase is properly configured and enabled"""
        return self.enabled and self.client is not None
    
    # User Management
    async def create_user(self, email: str, password: str, is_admin: bool = False) -> Dict:
        """Create a new user"""
        if not self.is_enabled():
            return {"error": "Database not available"}
        
        try:
            user_data = {
                "email": email,
                "password": password,  # In production, this should be hashed
                "is_admin": is_admin,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("users").insert(user_data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {"error": str(e)}
    
    async def get_user(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        if not self.is_enabled():
            return None
        
        try:
            result = self.client.table("users").select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        if not self.is_enabled():
            return []
        
        try:
            result = self.client.table("users").select("email, is_admin, created_at").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    async def save_email_to_users(self, email: str) -> Dict:
        """Save email address to users table if it doesn't exist"""
        if not self.is_enabled():
            return {"error": "Database not available"}
        
        try:
            # Check if user already exists
            existing_user = await self.get_user(email)
            if existing_user:
                logger.info(f"Email {email} already exists in users table")
                return {"success": True, "message": "Email already exists", "existing": True}
            
            # Create new user entry with email only (no password for email-only users)
            user_data = {
                "email": email,
                "password": None,  # No password for email-only users
                "is_admin": False,
                "created_at": datetime.now().isoformat(),
                "email_only": True  # Flag to indicate this is an email-only user
            }
            
            result = self.client.table("users").insert(user_data).execute()
            logger.info(f"Email {email} saved to users table successfully")
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"Error saving email to users table: {e}")
            return {"error": str(e)}
    
    # Dataset Management
    async def store_dataset(self, filename: str, data: pd.DataFrame, metadata: Dict = None) -> Dict:
        """Store dataset in Supabase"""
        if not self.is_enabled():
            return {"error": "Database not available"}
        
        try:
            # Store dataset metadata
            dataset_metadata = {
                "filename": filename,
                "rows": len(data),
                "columns": list(data.columns),
                "upload_date": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Insert metadata
            metadata_result = self.client.table("datasets").insert(dataset_metadata).execute()
            dataset_id = metadata_result.data[0]["id"]
            
            # Store actual data rows
            data_records = []
            for index, row in data.iterrows():
                record = {
                    "dataset_id": dataset_id,
                    "row_index": index,
                    "data": row.to_dict()
                }
                data_records.append(record)
            
            # Insert in batches to avoid size limits
            batch_size = 1000
            for i in range(0, len(data_records), batch_size):
                batch = data_records[i:i + batch_size]
                self.client.table("dataset_rows").insert(batch).execute()
            
            return {"success": True, "dataset_id": dataset_id}
        except Exception as e:
            logger.error(f"Error storing dataset: {e}")
            return {"error": str(e)}
    
    async def get_dataset(self, dataset_id: int = None, filename: str = None) -> Optional[pd.DataFrame]:
        """Retrieve dataset from Supabase"""
        if not self.is_enabled():
            return None
        
        try:
            # Get dataset metadata
            if dataset_id:
                metadata_result = self.client.table("datasets").select("*").eq("id", dataset_id).execute()
            elif filename:
                metadata_result = self.client.table("datasets").select("*").eq("filename", filename).order("upload_date", desc=True).limit(1).execute()
            else:
                # Get most recent dataset
                metadata_result = self.client.table("datasets").select("*").order("upload_date", desc=True).limit(1).execute()
            
            if not metadata_result.data:
                return None
            
            dataset_metadata = metadata_result.data[0]
            dataset_id = dataset_metadata["id"]
            
            # Get dataset rows
            rows_result = self.client.table("dataset_rows").select("*").eq("dataset_id", dataset_id).order("row_index").execute()
            
            if not rows_result.data:
                return None
            
            # Convert to DataFrame
            data_list = [row["data"] for row in rows_result.data]
            df = pd.DataFrame(data_list)
            
            return df
        except Exception as e:
            logger.error(f"Error retrieving dataset: {e}")
            return None
    
    async def get_latest_dataset(self) -> Optional[pd.DataFrame]:
        """Get the most recently uploaded dataset"""
        return await self.get_dataset()
    
    async def list_datasets(self) -> List[Dict]:
        """List all datasets"""
        if not self.is_enabled():
            return []
        
        try:
            result = self.client.table("datasets").select("id, filename, rows, upload_date").order("upload_date", desc=True).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            return []
    
    # Model Management
    async def store_model_metadata(self, model_info: Dict) -> Dict:
        """Store model training metadata"""
        if not self.is_enabled():
            return {"error": "Database not available"}
        
        try:
            model_data = {
                **model_info,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("model_metadata").insert(model_data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"Error storing model metadata: {e}")
            return {"error": str(e)}
    
    async def get_latest_model_metadata(self) -> Optional[Dict]:
        """Get the latest model metadata"""
        if not self.is_enabled():
            return None
        
        try:
            result = self.client.table("model_metadata").select("*").order("created_at", desc=True).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting model metadata: {e}")
            return None
    
    # Predictions Storage
    async def store_prediction(self, user_email: str, input_data: Dict, prediction: float, confidence: float) -> Dict:
        """Store a prediction result"""
        if not self.is_enabled():
            return {"error": "Database not available"}
        
        try:
            prediction_data = {
                "user_email": user_email,
                "input_data": input_data,
                "prediction": prediction,
                "confidence": confidence,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("predictions").insert(prediction_data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
            return {"error": str(e)}
    
    async def get_user_predictions(self, user_email: str, limit: int = 50) -> List[Dict]:
        """Get predictions for a specific user"""
        if not self.is_enabled():
            return []
        
        try:
            result = self.client.table("predictions").select("*").eq("user_email", user_email).order("created_at", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting user predictions: {e}")
            return []
    
    async def store_email_report(self, recipient_email: str, report_data: Dict, email_status: str = "sent") -> Dict:
        """Store email report information"""
        if not self.is_enabled():
            return {"error": "Database not available"}
        
        try:
            email_report = {
                "recipient_email": recipient_email,
                "report_data": report_data,
                "email_status": email_status,  # "sent", "failed", "simulated"
                "sent_at": datetime.now().isoformat()
            }
            
            result = self.client.table("email_reports").insert(email_report).execute()
            logger.info(f"Email report stored for {recipient_email}")
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"Error storing email report: {e}")
            return {"error": str(e)}
    
    async def get_email_reports(self, recipient_email: str = None, limit: int = 50) -> List[Dict]:
        """Get email reports, optionally filtered by recipient"""
        if not self.is_enabled():
            return []
        
        try:
            query = self.client.table("email_reports").select("*")
            if recipient_email:
                query = query.eq("recipient_email", recipient_email)
            
            result = query.order("sent_at", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting email reports: {e}")
            return []

# Global instance
supabase_client = SupabaseClient()

# Convenience functions
async def get_db_client() -> SupabaseClient:
    """Get the database client instance"""
    return supabase_client

async def init_database():
    """Initialize database tables if they don't exist"""
    if not supabase_client.is_enabled():
        logger.warning("Supabase not configured. Skipping database initialization.")
        return False
    
    try:
        # Note: In a real application, you would run these SQL commands in Supabase SQL editor
        # or use migrations. For now, we'll just log the required schema.
        
        logger.info("Database client ready. Make sure the following tables exist in Supabase:")
        logger.info("1. users (id, email, password, is_admin, created_at)")
        logger.info("2. datasets (id, filename, rows, columns, upload_date, metadata)")
        logger.info("3. dataset_rows (id, dataset_id, row_index, data)")
        logger.info("4. model_metadata (id, training_date, training_samples, test_samples, train_rmse, test_rmse, train_r2, test_r2, features, created_at)")
        logger.info("5. predictions (id, user_email, input_data, prediction, confidence, created_at)")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False
