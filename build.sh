#!/bin/bash
# Render build script

echo "Building MediCare+ Backend..."

# Install Python dependencies
pip install -r requirements-render.txt

# Create necessary directories
mkdir -p models
mkdir -p data
mkdir -p logs

echo "Build completed successfully"
