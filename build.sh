#!/bin/bash
# Exit immediately if any command exits with a non-zero status
set -e
echo "=== Starting Django Build Process ==="

# 1. Install project dependencies
echo "Installing dependencies from requirements.txt..."
python3 -m pip install -r requirements.txt

# 2. Clear out old static files and collect fresh ones
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

# 3. Apply database migrations to Neon PostgreSQL
echo "Running database migrations..."
python3 manage.py migrate --noinput

echo "=== Build Process Completed Successfully! ==="
