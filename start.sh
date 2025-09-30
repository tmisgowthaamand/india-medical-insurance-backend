#!/bin/bash
# Render startup script for MediCare+ Backend - Optimized for fast startup

echo "🏥 Starting MediCare+ Backend on Render..."

# Set default port if not provided
PORT=${PORT:-8001}
echo "Using port: $PORT"

# Create necessary directories
mkdir -p models data

# Quick startup - skip model training on startup to get server running fast
echo "🚀 Quick startup mode - server will train model in background"

# Create minimal fallback model quickly if none exists
if [ ! -f "models/model_pipeline.pkl" ]; then
    echo "Creating minimal model for immediate startup..."
    python -c "
import joblib
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import os

try:
    # Create minimal dummy model for immediate startup
    model = RandomForestRegressor(n_estimators=5, random_state=42, max_depth=3)
    X_dummy = np.random.rand(50, 6)  # Minimal training data
    y_dummy = np.random.rand(50) * 50000
    model.fit(X_dummy, y_dummy)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/model_pipeline.pkl')
    print('✅ Quick startup model created')
except Exception as e:
    print(f'⚠️ Quick model creation failed: {e}')
"
fi

# Start the application immediately
echo "🚀 Starting FastAPI server on port $PORT..."
echo "Environment: ${ENVIRONMENT:-production}"
echo "Supabase URL: ${SUPABASE_URL:0:50}..."

# Use exec to replace the shell process with optimized settings
exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 30 --access-log