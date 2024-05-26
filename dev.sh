#!/bin/bash
# Activate the virtual environment
source venv/bin/activate

# Setup jq
source setup.sh

cd ./app

# Set the config.json variables
source ../setvars.sh

pip3 -r requirements.txt

# Disable __pycache__'ing
export PYTHONDONTWRITEBYTECODE=1

# Start the sidecar
uvicorn main:app --port "$SIDECAR_PORT" --reload
