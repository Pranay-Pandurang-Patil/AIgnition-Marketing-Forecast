#!/bin/bash

DATA_DIR=${1:-data}
MODEL_PATH=${2:-pickle/model.pkl}
OUTPUT_PATH=${3:-output/predictions.csv}

echo "=========================================="
echo "AIgnition Forecast Pipeline"
echo "=========================================="

python src/predict.py

echo "=========================================="
echo "Forecast Complete"
echo "Predictions saved to $OUTPUT_PATH"
echo "=========================================="