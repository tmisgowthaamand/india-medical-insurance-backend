#!/bin/bash
# Render build script

echo "Building MediCare+ Backend..."

# Install Python dependencies
pip install -r requirements.txt

# Create directories
mkdir -p models data

# Create sample data if needed
python -c "
try:
    from create_sample_data import create_sample_dataset
    create_sample_dataset()
    print('Sample dataset created')
except Exception as e:
    print(f'Could not create sample dataset: {e}')
"

# Pre-train compatible model
echo "Pre-training compatible model..."
python -c "
try:
    from fast_train import fast_train
    import os
    data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
    if data_files:
        model = fast_train(dataset_path=f'data/{data_files[0]}', model_type='fast_rf')
        if model:
            print('Compatible model pre-trained successfully')
        else:
            print('Model training returned None')
    else:
        print('No dataset found for pre-training')
except Exception as e:
    print(f'Pre-training failed: {e}')
    print('Model will be trained on first startup')
"

echo "Build completed successfully"