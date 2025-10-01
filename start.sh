#!/bin/bash
# Render startup script for MediCare+ Backend

echo "Starting MediCare+ Backend..."
echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Installing dependencies..."
    pip install -r requirements-render.txt
fi

# Start the application
echo "Starting FastAPI server..."
exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1
