#!/usr/bin/env python3
"""
Startup script for India Medical Insurance ML Dashboard
This script helps set up and run the application quickly.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        India Medical Insurance ML Dashboard                  ║
    ║                                                              ║
    ║        🏥 FastAPI + React + ML Dashboard                     ║
    ║        🤖 Random Forest Regressor                            ║
    ║        📊 Interactive Analytics                              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
            return True
    except FileNotFoundError:
        pass
    print("❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/")
    return False

def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    # Create virtual environment if it doesn't exist
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"])
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = venv_dir / "Scripts" / "activate.bat"
        pip_path = venv_dir / "Scripts" / "pip.exe"
        python_path = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        activate_script = venv_dir / "bin" / "activate"
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    # Install requirements
    print("📦 Installing Python dependencies...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    # Train initial model if not exists
    model_path = Path("models/model_pipeline.pkl")
    if not model_path.exists():
        print("🤖 Training initial ML model...")
        subprocess.run([str(python_path), "train.py"])
    
    # Create default admin user
    create_default_users()
    
    os.chdir("..")
    print("✅ Backend setup complete")
    return True

def create_default_users():
    """Create default users file"""
    users_file = Path("users.json")
    if not users_file.exists():
        from utils import hash_password
        from datetime import datetime
        
        default_users = {
            "admin": {
                "password": hash_password("admin123"),
                "created_at": datetime.now().isoformat(),
                "is_admin": True
            },
            "user": {
                "password": hash_password("user123"),
                "created_at": datetime.now().isoformat(),
                "is_admin": False
            }
        }
        
        with open(users_file, 'w') as f:
            json.dump(default_users, f, indent=2)
        
        print("👤 Created default users (admin/admin123, user/user123)")

def setup_frontend():
    """Set up the frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    
    # Install npm dependencies
    print("📦 Installing Node.js dependencies...")
    result = subprocess.run(["npm", "install"])
    
    os.chdir("..")
    
    if result.returncode == 0:
        print("✅ Frontend setup complete")
        return True
    else:
        print("❌ Frontend setup failed")
        return False

def start_application():
    """Start both backend and frontend"""
    print("\n🚀 Starting application...")
    
    # Start backend
    print("🔥 Starting backend server...")
    backend_process = None
    try:
        os.chdir("backend")
        if os.name == 'nt':  # Windows
            python_path = Path(".venv/Scripts/python.exe")
        else:  # Unix/Linux/macOS
            python_path = Path(".venv/bin/python")
        
        backend_process = subprocess.Popen([
            str(python_path), "-m", "uvicorn", "app:app", 
            "--host", "0.0.0.0", "--port", "8001", "--reload"
        ])
        os.chdir("..")
        
        # Start frontend
        print("🔥 Starting frontend server...")
        os.chdir("frontend")
        frontend_process = subprocess.Popen(["npm", "run", "dev"])
        os.chdir("..")
        
        print("\n" + "="*60)
        print("🎉 Application started successfully!")
        print("="*60)
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8001")
        print("📚 API Docs: http://localhost:8001/docs")
        print("="*60)
        print("\n👤 Default Login Credentials:")
        print("   Admin: admin@example.com / admin123")
        print("   User:  user@example.com / user123")
        print("\n🗄️  Database Integration:")
        print("   📊 Supabase: Check .env files for configuration")
        print("   📋 Setup Guide: See SUPABASE_SETUP_GUIDE.md")
        print("\n⏹️  Press Ctrl+C to stop the servers")
        print("="*60)
        
        # Wait for processes
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
            print("✅ Servers stopped")
    
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        if backend_process:
            backend_process.terminate()

def main():
    """Main function"""
    print_banner()
    
    # Check prerequisites
    check_python_version()
    if not check_node_version():
        return
    
    # Setup
    if not setup_backend():
        return
    
    if not setup_frontend():
        return
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()
