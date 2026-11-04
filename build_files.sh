#!/bin/bash
set -e

echo "=== Building The Sunwai for Vercel ==="

# Install dependencies
python3 -m pip install -r requirements.txt

# Run database migrations
python3 manage.py migrate --noinput

# Seed initial portal data
python3 manage.py seed_sunwai

# Collect static files for whitenoise
python3 manage.py collectstatic --noinput --clear

echo "=== Build Complete ==="
