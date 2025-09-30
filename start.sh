#!/bin/bash
# Render startup script for MediCare+ Backend

echo "🏥 Starting MediCare+ Backend on Render..."

# Set default port if not provided
PORT=${PORT:-8001}
echo "Using port: $PORT"

# Create necessary directories
mkdir -p models data

# Create sample dataset if needed
echo "📊 Checking for dataset..."
if [ ! -f "data/sample_medical_insurance_data.csv" ]; then
    echo "Creating sample dataset..."
    python -c "
try:
    from create_sample_data import create_sample_dataset
    create_sample_dataset()
    print('✅ Sample dataset created')
except Exception as e:
    print(f'⚠️ Could not create sample dataset: {e}')
    print('Will use fallback data')
"
fi

# Train model if needed (with error handling)
echo "🤖 Checking for ML model..."
if [ ! -f "models/model_pipeline.pkl" ]; then
    echo "Training model for deployment..."
    python -c "
try:
    from fast_train import fast_train
    import os
    
    # Look for any CSV file in data directory
    data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
    if data_files:
        print(f'Training with dataset: {data_files[0]}')
        model = fast_train(dataset_path=f'data/{data_files[0]}', model_type='fast_rf')
        print('✅ Model trained successfully')
    else:
        print('⚠️ No dataset found, will use fallback model')
        # Create a minimal fallback model
        import joblib
        from sklearn.ensemble import RandomForestRegressor
        import numpy as np
        
        # Create dummy model
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        X_dummy = np.random.rand(100, 6)  # 6 features
        y_dummy = np.random.rand(100) * 50000
        model.fit(X_dummy, y_dummy)
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(model, 'models/model_pipeline.pkl')
        print('✅ Fallback model created')
        
except Exception as e:
    print(f'⚠️ Model training failed: {e}')
    print('Application will start without pre-trained model')
"
fi

# Start the application with error handling
echo "🚀 Starting FastAPI server on port $PORT..."
echo "Environment: ${ENVIRONMENT:-production}"
echo "Supabase URL: ${SUPABASE_URL:0:50}..."

# Use exec to replace the shell process
exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1