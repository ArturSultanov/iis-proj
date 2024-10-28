#!/bin/bash

echo "Clearing pycache..."
find . -type d -name "__pycache__" -exec rm -rf {} +


# Check if a virtual environment already exists
if [[ -d ".venv" ]]; then
    echo "Creating a new virtual env..."
    python3 -m venv .venv
fi

# Check if the virtual environment is activated

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Activating the virtual env..."
    source .venv/bin/activate
fi


if [[ -f "requirements.txt" ]]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please make sure it is in the current directory."
fi

# Keep the virtual environment activated in the current shell
exec "$SHELL"
