#!/bin/bash
# Render startup script for MediCare+ Backend

echo "Starting MediCare+ Backend on Render..."

# Create necessary directories
mkdir -p models data

# Check if we have a dataset
if [ ! -f "data/sample_medical_insurance_data.csv" ]; then
    echo "Creating sample dataset..."
    python -c "from create_sample_data import create_sample_dataset; create_sample_dataset()"
fi

# Force retrain with compatible model on first run
if [ ! -f "models/model_pipeline.pkl" ]; then
    echo "Training compatible model for first deployment..."
    python -c "
from fast_train import fast_train
import os
data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
if data_files:
    model = fast_train(dataset_path=f'data/{data_files[0]}', model_type='fast_rf')
    print('Compatible model trained for Render deployment')
else:
    print('No dataset found')
"
fi

# Start the application
echo "Starting FastAPI server..."
exec uvicorn app:app --host 0.0.0.0 --port $PORT