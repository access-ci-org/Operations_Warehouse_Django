#!/bin/bash
set -e

echo "Running migrations..."
ls -la
python manage.py migrate --noinput

echo "Running tests..."
pytest "$@"
