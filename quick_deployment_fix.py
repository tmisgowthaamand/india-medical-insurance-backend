#!/usr/bin/env python3
"""
Quick Deployment Fix for Render Backend
Focuses on essential fixes without complex database operations
"""

import os
import sys
import subprocess
from pathlib import Path

def create_startup_script():
    """Create a startup script for Render"""
    print("🚀 Creating startup script...")
    
    startup_content = """#!/bin/bash
# Render startup script for MediCare+ Backend

echo "🚀 Starting MediCare+ Backend..."
echo "📊 Environment: $ENVIRONMENT"
echo "🔗 Port: $PORT"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements-render.txt
fi

# Start the application
echo "🎯 Starting FastAPI server..."
exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1
"""
    
    try:
        with open("start.sh", "w") as f:
            f.write(startup_content)
        
        # Make executable
        os.chmod("start.sh", 0o755)
        print("✅ Created start.sh")
        return True
    except Exception as e:
        print(f"❌ Error creating startup script: {e}")
        return False

def update_app_for_production():
    """Update app.py for better production compatibility"""
    print("🔧 Updating app.py for production...")
    
    try:
        # Read current app.py
        with open("app.py", "r") as f:
            content = f.read()
        
        # Add health check if not present
        if "/health" not in content:
            health_check = '''
@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "service": "MediCare+ Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
'''
            # Add import for datetime if not present
            if "from datetime import datetime" not in content:
                content = "from datetime import datetime\n" + content
            
            # Add health check before the main block
            content = content.replace(
                'if __name__ == "__main__":',
                health_check + '\nif __name__ == "__main__":'
            )
            
            with open("app.py", "w") as f:
                f.write(content)
            
            print("✅ Added health check endpoint")
        
        return True
    except Exception as e:
        print(f"❌ Error updating app.py: {e}")
        return False

def create_render_build_script():
    """Create build script for Render"""
    print("📦 Creating build script...")
    
    build_content = """#!/bin/bash
# Render build script

echo "🔨 Building MediCare+ Backend..."

# Install Python dependencies
pip install -r requirements-render.txt

# Create necessary directories
mkdir -p models
mkdir -p data
mkdir -p logs

echo "✅ Build completed successfully"
"""
    
    try:
        with open("build.sh", "w") as f:
            f.write(build_content)
        
        os.chmod("build.sh", 0o755)
        print("✅ Created build.sh")
        return True
    except Exception as e:
        print(f"❌ Error creating build script: {e}")
        return False

def verify_essential_files():
    """Verify all essential files are present"""
    print("🔍 Verifying essential files...")
    
    essential_files = [
        "app.py",
        "requirements-render.txt",
        "Procfile",
        "render.yaml"
    ]
    
    missing_files = []
    for file in essential_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All essential files present")
    return True

def main():
    """Main quick fix function"""
    print("⚡ Quick Deployment Fix for Render Backend")
    print("=" * 50)
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Create startup script
    if create_startup_script():
        success_count += 1
    
    # Step 2: Update app.py
    if update_app_for_production():
        success_count += 1
    
    # Step 3: Create build script
    if create_render_build_script():
        success_count += 1
    
    # Step 4: Verify files
    if verify_essential_files():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("\n🎉 Quick fix completed!")
        print("\n📋 Deployment Instructions:")
        print("1. Commit all changes to your repository")
        print("2. Push to GitHub/GitLab")
        print("3. In Render dashboard:")
        print("   - Build Command: ./build.sh")
        print("   - Start Command: ./start.sh")
        print("4. Set environment variables in Render dashboard")
        print("\n🔗 Test URLs after deployment:")
        print("   - Health: https://your-app.onrender.com/health")
        print("   - Docs: https://your-app.onrender.com/docs")
        
        return True
    else:
        print("\n❌ Some steps failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
