#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./install.sh first to set up the application."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run the Flask application with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
