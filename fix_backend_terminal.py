#!/usr/bin/env python3
"""
Backend Terminal Fix Script
Comprehensive solution for backend terminal and process issues
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_status(message, status="INFO"):
    """Print status message with formatting"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")

def kill_existing_processes():
    """Kill any existing Python/uvicorn processes"""
    print_status("Killing existing Python processes...")
    
    try:
        # Kill Python processes on common ports
        for port in [8000, 8001, 5000]:
            try:
                subprocess.run([
                    "powershell", "-Command", 
                    f"Get-Process | Where-Object {{$_.ProcessName -eq 'python'}} | Stop-Process -Force"
                ], capture_output=True, timeout=10)
            except:
                pass
        
        # Kill processes using specific ports
        for port in [8000, 8001]:
            try:
                subprocess.run([
                    "powershell", "-Command",
                    f"netstat -ano | findstr :{port} | ForEach-Object {{$_.Split(' ')[-1]}} | ForEach-Object {{taskkill /PID $_ /F}}"
                ], capture_output=True, timeout=10)
            except:
                pass
                
        print_status("Existing processes killed", "SUCCESS")
        time.sleep(2)
        
    except Exception as e:
        print_status(f"Error killing processes: {e}", "WARNING")

def check_python_environment():
    """Check and fix Python environment"""
    print_status("Checking Python environment...")
    
    # Check if we're in the right directory
    backend_dir = Path("c:/Users/Admin/CascadeProjects/india-medical-insurance-dashboard/backend")
    if not backend_dir.exists():
        print_status("Backend directory not found!", "ERROR")
        return False
    
    os.chdir(backend_dir)
    print_status(f"Working directory: {os.getcwd()}")
    
    # Check Python version
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        print_status(f"Python version: {result.stdout.strip()}")
    except Exception as e:
        print_status(f"Python check failed: {e}", "ERROR")
        return False
    
    return True

def setup_virtual_environment():
    """Setup and activate virtual environment"""
    print_status("Setting up virtual environment...")
    
    venv_path = Path(".venv")
    
    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print_status("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], 
                          check=True, timeout=60)
            print_status("Virtual environment created", "SUCCESS")
        except Exception as e:
            print_status(f"Failed to create venv: {e}", "ERROR")
            return False
    
    # Activate virtual environment (Windows)
    activate_script = venv_path / "Scripts" / "activate.bat"
    if activate_script.exists():
        print_status("Virtual environment found", "SUCCESS")
        return True
    else:
        print_status("Virtual environment activation script not found", "ERROR")
        return False

def install_dependencies():
    """Install required dependencies"""
    print_status("Installing dependencies...")
    
    # Use the virtual environment Python
    venv_python = Path(".venv/Scripts/python.exe")
    if not venv_python.exists():
        venv_python = sys.executable
    
    try:
        # Upgrade pip first
        subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, timeout=120)
        
        # Install requirements
        subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, timeout=300)
        
        print_status("Dependencies installed successfully", "SUCCESS")
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install dependencies: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"Unexpected error during installation: {e}", "ERROR")
        return False

def check_environment_variables():
    """Check and load environment variables"""
    print_status("Checking environment variables...")
    
    env_file = Path(".env")
    if env_file.exists():
        print_status("Found .env file", "SUCCESS")
        
        # Load and display key variables (without sensitive data)
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        key = line.split('=')[0].strip()
                        if key in ['SUPABASE_URL', 'ALLOWED_ORIGINS']:
                            print_status(f"  {key} is set")
                        elif 'KEY' in key or 'SECRET' in key:
                            print_status(f"  {key} is set (hidden)")
        except Exception as e:
            print_status(f"Error reading .env file: {e}", "WARNING")
    else:
        print_status(".env file not found", "WARNING")
    
    return True

def start_backend_server():
    """Start the backend server"""
    print_status("Starting backend server...")
    
    venv_python = Path(".venv/Scripts/python.exe")
    if not venv_python.exists():
        venv_python = sys.executable
    
    try:
        # Start uvicorn server
        cmd = [
            str(venv_python), "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8001", 
            "--reload"
        ]
        
        print_status(f"Running command: {' '.join(cmd)}")
        
        # Start the process in the background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Wait a bit for the server to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print_status("Backend server started successfully!", "SUCCESS")
            print_status("Server is running on http://localhost:8001", "SUCCESS")
            return process
        else:
            stdout, stderr = process.communicate()
            print_status(f"Server failed to start. Error: {stderr}", "ERROR")
            return None
            
    except Exception as e:
        print_status(f"Failed to start server: {e}", "ERROR")
        return None

def test_backend_connection():
    """Test if backend is responding"""
    print_status("Testing backend connection...")
    
    try:
        response = requests.get("http://localhost:8001/", timeout=10)
        if response.status_code == 200:
            print_status("Backend is responding correctly!", "SUCCESS")
            return True
        else:
            print_status(f"Backend returned status code: {response.status_code}", "WARNING")
            return False
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to backend - server may not be running", "ERROR")
        return False
    except Exception as e:
        print_status(f"Error testing connection: {e}", "ERROR")
        return False

def create_startup_script():
    """Create a startup script for easy server management"""
    print_status("Creating startup script...")
    
    startup_script = """@echo off
echo Starting MediCare+ Backend Server...
cd /d "c:\\Users\\Admin\\CascadeProjects\\india-medical-insurance-dashboard\\backend"

echo Activating virtual environment...
call .venv\\Scripts\\activate.bat

echo Starting server on port 8001...
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

pause
"""
    
    try:
        with open("start_backend.bat", "w") as f:
            f.write(startup_script)
        print_status("Startup script created: start_backend.bat", "SUCCESS")
    except Exception as e:
        print_status(f"Failed to create startup script: {e}", "WARNING")

def main():
    """Main fix function"""
    print_status("=" * 60)
    print_status("BACKEND TERMINAL FIX SCRIPT")
    print_status("=" * 60)
    
    # Step 1: Kill existing processes
    kill_existing_processes()
    
    # Step 2: Check Python environment
    if not check_python_environment():
        print_status("Python environment check failed", "ERROR")
        return False
    
    # Step 3: Setup virtual environment
    if not setup_virtual_environment():
        print_status("Virtual environment setup failed", "ERROR")
        return False
    
    # Step 4: Install dependencies
    if not install_dependencies():
        print_status("Dependency installation failed", "ERROR")
        return False
    
    # Step 5: Check environment variables
    check_environment_variables()
    
    # Step 6: Create startup script
    create_startup_script()
    
    # Step 7: Start backend server
    process = start_backend_server()
    if not process:
        print_status("Failed to start backend server", "ERROR")
        return False
    
    # Step 8: Test connection
    time.sleep(3)  # Give server more time to start
    if test_backend_connection():
        print_status("=" * 60)
        print_status("BACKEND FIX COMPLETED SUCCESSFULLY!", "SUCCESS")
        print_status("=" * 60)
        print_status("Backend server is running on: http://localhost:8001")
        print_status("API documentation: http://localhost:8001/docs")
        print_status("Use 'start_backend.bat' to restart the server in future")
        print_status("Press Ctrl+C to stop the server")
        
        # Keep the script running to monitor the server
        try:
            while True:
                time.sleep(10)
                if process.poll() is not None:
                    print_status("Server process has stopped", "WARNING")
                    break
        except KeyboardInterrupt:
            print_status("Stopping server...", "INFO")
            process.terminate()
            
        return True
    else:
        print_status("Backend connection test failed", "ERROR")
        if process:
            process.terminate()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print_status("Fix script completed with errors", "ERROR")
        sys.exit(1)
    else:
        print_status("Fix script completed successfully", "SUCCESS")
