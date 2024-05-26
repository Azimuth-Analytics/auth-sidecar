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
        # MacOS
        if ! command -v brew &> /dev/null; then
            echo "Homebrew is not installed. Please install Homebrew first."
            exit 1
        else
            brew install jq
        fi
    else
        echo "Unsupported operating system. Manual installation required."
        exit 1
    fi
}

check_jq