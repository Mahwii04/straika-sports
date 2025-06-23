#!/usr/bin/env bash
set -o errexit

# Install dependencies including gunicorn
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database if needed
if [ ! -d "migrations" ]; then
    flask db init
fi

# Generate and apply migrations
flask db migrate -m "Render migration" || true
flask db upgrade