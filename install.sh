#!/bin/bash

echo "=========================================="
echo "Shut the Box - Installation Script"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python version: $PYTHON_VERSION"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ ! -d "venv" ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install pip
echo ""
echo "Installing pip..."
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
rm get-pip.py

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    # Generate a random secret key
    SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
    sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
    echo "Generated random SECRET_KEY in .env file"
fi

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "To run the application:"
echo "  ./run_app.sh"
echo ""
echo "The application will be available at http://localhost:8000"
echo ""
