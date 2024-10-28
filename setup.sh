#!/bin/bash

echo "Clearing pycache..."
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "Creating a new virtual env..."
python3 -m venv .venv

source .venv/bin/activate

if [[ -f "requirements.txt" ]]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please make sure it is in the current directory."
fi

# Keep the virtual environment activated in the current shell
exec "$SHELL"
