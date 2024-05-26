#!/bin/bash

# Function to check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo "jq could not be found, installing..."
        install_jq
    else
        echo "jq is already installed."
    fi
}

# Function to install jq based on the OS type
install_jq() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f /etc/debian_version ]]; then
            # Debian-based system
            sudo apt-get update
            sudo apt-get install -y jq
        elif [[ -f /etc/redhat-release ]]; then
            # RedHat-based system
            sudo yum install -y jq
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            echo "Homebrew is not installed. Please install Homebrew first."
            exit 1
        else
            brew install jq
        fi
    else
        echo "Unsupported OS. Please install jq manually."
        exit 1
    fi
}
# Activate the virtual environment
source venv/bin/activate

# Change to the app directory
cd app/

# Check if jq is installed, and install if necessary
check_jq

# Path to the JSON file
json_file="config.json"

# Extract the sidecar port using jq
SIDECAR_PORT=$(jq -r '.sidecar_port' "$json_file")

# Export environment variables
export PYTHONDONTWRITEBYTECODE=1

# Start the FastAPI app with uvicorn
uvicorn main:app --port "$SIDECAR_PORT" --reload
