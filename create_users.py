#!/usr/bin/env python3
"""
Create default users for the application
"""

import json
from datetime import datetime
from utils import hash_password

def create_default_users():
    """Create default users with email addresses"""
    
    default_users = {
        "admin@example.com": {
            "password": hash_password("admin123"),
            "created_at": datetime.now().isoformat(),
            "is_admin": True
        },
        "user@example.com": {
            "password": hash_password("user123"),
            "created_at": datetime.now().isoformat(),
            "is_admin": False
        },
        "demo@example.com": {
            "password": hash_password("demo123"),
            "created_at": datetime.now().isoformat(),
            "is_admin": False
        }
    }
    
    with open('users.json', 'w') as f:
        json.dump(default_users, f, indent=2)
    
    print("✅ Default users created successfully!")
    print("📧 Login credentials:")
    print("   Admin: admin@example.com / admin123")
    print("   User:  user@example.com / user123")
    print("   Demo:  demo@example.com / demo123")

if __name__ == "__main__":
    create_default_users()
