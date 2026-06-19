#!/bin/bash
# Exit immediately if any command exits with a non-zero status
set -e
echo "=== Starting Django Build Process ==="
export BUILDING_STATIC=True

# 1. Install project dependencies in a virtual environment
echo "Setting up Python environment..."
if command -v uv &> /dev/null; then
    echo "Using uv to create a Python 3.12 virtual environment..."
    uv venv .venv --python 3.12
    source .venv/bin/activate
    echo "Installing dependencies using uv..."
    uv pip install -r requirements.txt
else
    echo "uv not found, using python3 -m venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies using pip..."
    python3 -m pip install -r requirements.txt --break-system-packages
fi

# 2. Clear out old static files and collect fresh ones
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

# 3. Apply database migrations to Neon PostgreSQL
echo "Running database migrations..."
python3 manage.py migrate --noinput

echo "=== Build Process Completed Successfully! ==="
